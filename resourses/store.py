from flask.views import MethodView
from flask_smorest import Blueprint, abort

from schemas import StoreSchema
from db import stores
from utils import get_unique_id

blp = Blueprint("Stores", __name__, description="Operations on stores")


@blp.route("/store")
class StoreList(MethodView):
    @staticmethod
    @blp.response(200, StoreSchema(many=True))
    def get():
        return stores.values()

    @staticmethod
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(store_data):
        # create store with unique id
        store_id = get_unique_id()
        store = {
            "id": store_id,
            **store_data
        }
        # save to db and return
        stores[store_id] = store
        return store


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @staticmethod
    @blp.response(200, StoreSchema)
    def get(store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(404, message=F"Store with id: {store_id} not found")

    @staticmethod
    def delete(store_id):
        try:
            del stores[store_id]
            return {"message": "Item deleted."}
        except KeyError:
            abort(404, f'Store with id: {store_id} not found')
