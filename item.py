from flask_jwt import jwt_required
from flask_restful import Resource, reqparse
import sqlite3


def get_item_by_name(name):
    return next(filter(lambda x: x['name'] == name, items), None)


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This filed cannot be left blank')

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items WHERE name = ?"

        result = cursor.execute(query, (name,))
        row = result.fetchone()

        connection.close()
        return row

    @jwt_required()
    def get(self, name):
        row = self.find_by_name(name)

        if row:
            return {"item": {"name": row[0], 'price': row[1]}}
        return {'message': 'Item not found'}, 404

    @classmethod
    def insert(cls, item):

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO items VALUES (?, ?)"
        cursor.execute(query, (item['name'], item['price']))

        connection.commit()
        connection.close()

    def post(self, name):
        if self.find_by_name(name):
            return {'message': 'item {} already created'.format(name)}, 400

        data = Item.parser.parse_args()
        item = {'name': name, 'price': data['price']}

        try:
            self.insert(item)
        except:
            return {"message": "An error occured inserting the item."}, 500

        return item, 201

    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name = ?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()

        return {'message': 'Item deleted'}

    @classmethod
    def update(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "UPDATE items SET price = ? WHERE name = ?"
        cursor.execute(query, (item['price'], item['name']))

        connection.commit()
        connection.close()

    def put(self, name):
        data = Item.parser.parse_args()

        item = self.find_by_name(name)
        updated_item = {'name': name, 'price': data['price']}
        try:
            if not item:
                self.insert(updated_item)
            else:
                self.update(updated_item)
        except:
            return {"message": "An error occured updating the item."}, 500
        return updated_item


class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({
                'name': row[0],
                'price': row[1]
            })
        connection.close()

        return {'items': items}
