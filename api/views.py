from flask import Blueprint, jsonify, request, render_template
from . import db
from .models import Item

api = Blueprint('api', __name__)

@api.route('/')
def my_index():
  return render_template('index.html', token='Hello Flask+React')

@api.route('/api/add_item', methods=['POST'])
def add_item():
  item_data = request.get_json()

  new_item = Item(name=item_data['name'], description=item_data['description'])

  db.session.add(new_item)
  db.session.commit()

  return 'Done', 201

@api.route('/api/items')
def items():
  items_list = Item.query.all()
  items = []

  for item in items_list:
    items.append({ 'name': item.name, 'description': item.description })

  return jsonify({ 'items': items })
