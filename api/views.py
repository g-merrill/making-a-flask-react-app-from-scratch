from flask import Blueprint, jsonify

api = Blueprint('api', __name__)

@api.route('/add_item', methods=['POST'])
def add_item():

  return 'Done', 201

@api.route('/items')
def items():

  items = []

  return jsonify({ 'items': items })