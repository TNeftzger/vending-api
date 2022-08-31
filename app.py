from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
import os
from flask_marshmallow import Marshmallow


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'vending.db')


db = SQLAlchemy(app)
ma = Marshmallow(app)


# Database Creation
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


# Database Deletion
@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


# Database Seeding
@app.cli.command('db_seed')
def db_seed():
    coke = Soda(soda_name='Coke',
                     soda_cost=2,
                     soda_count=5)

    pepsi = Soda(soda_name='Pepsi',
                     soda_cost=2,
                     soda_count=5)

    dr_pepper = Soda(soda_name='Dr. Pepper',
                     soda_cost=2,
                     soda_count=5)

    db.session.add(coke)
    db.session.add(pepsi)
    db.session.add(dr_pepper)

    db.session.add(coin)
    db.session.commit()
    print('Database seeded!')


# Not on the test sheet but setup a GET for testing purposes
@app.route('/', methods=['GET'])
def coin():
    coin_get = Money.query.filter_by(coin_id=1).first()
    result = coin_schema.dump(coin_get)
    #return jsonify(message="You have " + str(result["coin"]) + " coins.")
    return Response(headers={'X-Coins: ': str(result["coin"])}), 204


# PUT functionality for / endpoint
@app.route('/', methods=['PUT'])
def update_coin():
    money = Money.query.filter_by(coin_id=1).first()
    if money:
        money.coin = money.coin + int(request.form['coin'])
        db.session.commit()
        return Response(headers={'X-Coins: ': str(money.coin)}), 204
    else:
        return jsonify(message="You must enter only one coin"), 404


# DELETE functionality for / endpoint
@app.route('/', methods=['DELETE'])
def reset_coin():
    money = Money.query.filter_by(coin_id=1).first()
    if money:
        change = money.coin
        db.session.delete(money.coin)
        db.session.commit()
        return Response(headers={'X-Coins: ': str(change)}), 204
    else:
        return jsonify(message="You must enter only one coin"), 404


# Complete Inventory Endpoint
@app.route('/inventory', methods=['GET'])
def inventory():
    sodas_list = Soda.query.all()
    result = sodas_schema.dump(sodas_list)
    return jsonify(result)


# Single Soda Item Endpoint
@app.route('/inventory/<int:soda_id>', methods=["GET"])
def soda_details(soda_id: int):
    soda = Soda.query.filter_by(soda_id=soda_id).first()
    if soda:
        result = soda_schema.dump(soda)
        return jsonify(result)
    else:
        return jsonify(message="No such item in inventory"), 404


# PUT functionality for /inventory/id endpoint
@app.route('/inventory/<int:soda_id>', methods=['PUT'])
def update_inventory(soda_id: int):
    money = Money.query.filter_by(coin_id=1).first()
    update_inventory = Soda.query.filter_by(soda_id=soda_id).first()
    if update_inventory.soda_count > 0:
        items_delivered = int(money.coin / 2)
        returned_coins = money.coin % 2
        update_inventory.soda_count = update_inventory.soda_count - items_delivered
        db.session.commit()
        if update_inventory.soda_count <= 0:
            return jsonify(message="This product is out of stock."), 404
        return jsonify(message={'quantity': str(items_delivered)}), 204
    else:
        return jsonify(message="Out of stock! Choose a different soda."), 404


# Vending Database Model
class Money(db.Model): # Money database in different types of currency allowed
    __tablename__ = 'money'
    coin_id = Column(Integer, primary_key=True)
    coin = Column(Integer)


class Soda(db.Model): # Soda database
    __tablename__ = 'soda_inventory'
    soda_id = Column(Integer, primary_key=True)
    soda_name = Column(String)
    soda_cost = Column(Integer)
    soda_count = Column(Integer)


class MoneySchema(ma.Schema):
    class Meta:
        fields = ('coin_id', 'coin')


class SodaSchema(ma.Schema):
    class Meta:
        fields = ('soda_id', 'soda_name', 'soda_cost', 'soda_count')


coin_schema = MoneySchema()

soda_schema = SodaSchema()
sodas_schema = SodaSchema(many=True)


if __name__ == '__main__':
    app.run()
