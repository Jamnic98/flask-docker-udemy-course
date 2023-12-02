from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import items
from schemas import ItemSchema, ItemUpdateSchema
from utils import get_unique_id

blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item")
class ItemList(MethodView):
    @staticmethod
    @blp.response(200, ItemSchema(many=True))
    def get():
        return items.values(), 200

    @staticmethod
    @blp.arguments(ItemSchema)
    @blp.response(200, ItemSchema)
    def post(item_data):
        for item in items.values():
            if (
                    item_data["name"] == item["name"]
                    and item_data["store_id"] == item["store_id"]
            ):
                abort(400, message="Item already exists")

        # create item with unique id
        item_id = get_unique_id()
        item = {
            "id": item_id,
            **item_data
        }
        # save to db and return new item
        items[item_id] = item
        return item, 201


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @staticmethod
    @blp.response(200, ItemSchema)
    def get(item_id):
        try:
            return items[item_id], 200
        except KeyError:
            abort(404, f'Item with id: {item_id} not found')

    @staticmethod
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(item_data, item_id):
        try:
            item = items[item_id]
            item |= item_data
            return item, 200

        except KeyError:
            abort(404, message="Item not found.")

    @staticmethod
    def delete(item_id):
        try:
            del items[item_id]
            return {"message": "Item deleted."}
        except KeyError:
            abort(404, f'Item with id: {item_id} not found')
