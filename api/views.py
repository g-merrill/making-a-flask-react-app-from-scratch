from flask import Blueprint, jsonify, request
from . import db
from .models import Item

api = Blueprint('api', __name__)

@api.route('/add_item', methods=['POST'])
def add_item():
  item_data = request.get_json()

  new_item = Item(name=item_data['name'], description=item_data['description'])

  db.session.add(new_item)
  db.session.commit()

  return 'Done', 201

@api.route('/items')
def items():
  items_list = Item.query.all()
  items = []

  for item in items_list:
    items.append({ 'name': item.name, 'description': item.description })

  return jsonify({ 'items': items })

# name = db.Column(db.String(50))
# description = db.Column(db.String(250))