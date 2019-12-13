from flask import Blueprint, jsonify, request
from . import db
from .models import Item

api = Blueprint('api', __name__)

@api.route('/api/items')
def items():
  items_list = Item.query.order_by(Item.id.desc())
  items = []

  for item in items_list:
    items.append({ 'name': item.name, 'description': item.description })

  return jsonify({ 'items': items })

@api.route('/api/add_item', methods=['POST'])
def add_item():
  item_data = request.get_json()

  new_item = Item(name=item_data['name'], description=item_data['description'])

  db.session.add(new_item)
  db.session.commit()

  return 'The POST request to this route worked!', 201