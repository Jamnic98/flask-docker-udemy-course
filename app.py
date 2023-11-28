import uuid
from flask import Flask, request
from flask_smorest import abort
from db import stores, items

app = Flask(__name__)


def get_unique_id():
    return uuid.uuid4().hex


# STORE
@app.get("/store")
def get_stores():
    return {"stores": list(stores.values())}, 200


@app.get("/item")
def get_items():
    return {"items": list(items.values())}, 200


@app.get("/store/<string:store_id>")
def get_store(store_id):
    try:
        return {"store": stores[store_id]}, 200
    except KeyError:
        abort(404, message=F"Store with id: {store_id} not found")


@app.post("/store")
def create_store():
    store_data = request.get_json()
    if "name" not in store_data:
        abort(400, "Missing 'name' in json request")
    # create store with unique id
    store_id = get_unique_id()
    store = {
        "id": store_id,
        **store_data
    }
    # save to db and return
    stores[store_id] = store
    return store, 201


@app.delete("/store/<string:store_id>")
def delete_store_by_id(store_id):
    try:
        del stores[store_id]
        return {"message": "Item deleted."}
    except KeyError:
        abort(404, f'Store with id: {store_id} not found')


# ITEMS
@app.post("/item")
def create_item():
    request_data = request.get_json()
    if (
        "price" not in request_data or
        "store_id" not in request_data or
        "name" not in request_data
    ):
        abort(400, message="Missing json data in request")

    if request_data["store_id"] not in stores:
        abort(404, message="Store not found")

    for item in items.values():
        if (
            request_data["name"] == item["name"]
                and request_data["store_id"] == item["store_id"]
        ):
            abort(400, message="Item already exists")

    store_id = request_data["store_id"]
    if store_id not in stores:
        abort(400, message=f"Store with id: {store_id}")

    # create item with unique id
    item_id = get_unique_id()
    item = {
        "id": item_id,
        **request_data
    }
    # save to db and return
    items[item_id] = item

    return item, 201


# delete item
@app.delete("/item/<string:item_id>")
def delete_item_by_id(item_id):
    try:
        del items[item_id]
        return {"message": "Item deleted."}
    except KeyError:
        abort(404, f'Item with id: {item_id} not found')


@app.put("/item/<string:item_id>")
def update_item_by_id(item_id):
    request_data = request.get_json()
    if "price" not in request_data or "name" not in request_data:
        abort(400, message="Bad request. Ensure correct data in payload")

    try:
        item = items[item_id]
        item |= request_data
        return item, 200

    except KeyError:
        abort(404, message="Item not found.")
