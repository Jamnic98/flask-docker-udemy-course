from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST

blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @staticmethod
    @blp.arguments(UserSchema)
    @blp.response(201, description="User registered successfully")
    def post(user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully"}


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @staticmethod
    @blp.response(200, UserSchema)
    def get(user_id):
        return UserModel.query.get_or_404(user_id)

    @staticmethod
    @blp.response(204, None)
    def delete(user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}


@blp.route("/login")
class UserLogin(MethodView):
    @staticmethod
    @blp.arguments(UserSchema)
    def post(user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)

            return {"access_token": access_token, "refresh_token": refresh_token}

        abort(401, description="Invalid credentials")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"message": "Logged out successfully"}


@blp.route("/refresh")
class UserRefreshToken(MethodView):
    @jwt_required(fresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}
