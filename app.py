from itertools import product
from flask import Flask, jsonify, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# INIT
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INIT DB
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100), unique=True)
    mail = db.Column(db.String(100), unique=True)
    image = db.Column(db.String(300))
    numberPhone = db.Column(db.String(300))
    password = db.Column(db.String)

    def __init__(self, nickname, mail, image, numberPhone, password):
        self.nickname = nickname
        self.mail = mail
        self.image = image
        self.numberPhone = numberPhone
        self.password = password


class ProductModel(db.Model):

    __tablename__ = "Products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(1000))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)
    category = db.Column(db.String(100))
    img = db.Column(db.String(300))

    def _init_(self, name, description, price, qty, img, category):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty
        self.img = img
        self.category = category

# SCHEMA


class ClientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nickname', 'mail', 'image', 'numberPhone', 'password')


class ProductModelSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description',
                  'price', 'qty', 'img', 'category')


# INIT SCHEMA
client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)

product_schema = ProductModelSchema()
products_schema = ProductModelSchema(many=True)


@app.route('/add_client', methods=['POST'])
def add_client():
    nickname = request.json['nickname']
    mail = request.json['mail']
    image = request.json['image']
    numberPhone = request.json['numberPhone']
    password = request.json['password']
    new_client = Client(nickname=nickname, mail=mail, image=image,
                        numberPhone=numberPhone, password=password)
    db.session.add(new_client)
    db.session.commit()
    return {"results": "ok"}


@app.route('/login', methods=['POST'])
def login():
    nickname = request.json['nickname']
    password = request.json['password']
    user = Client.query.filter_by(nickname=nickname).first()
    if user:
        if password == user.password:
            client = client_schema.dump(user)
            return jsonify(client)


@app.route('/clients', methods=['GET'])
def getAllClients():
    Clients = Client.query.all()
    result = clients_schema.dump(Clients)
    return jsonify(result)

# WEB


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('createpage.html')

    if request.method == 'POST':

        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        qty = request.form['qty']
        category = request.form['category']
        img = request.form['img']
        products = ProductModel(
            name=name,
            description=description,
            price=price,
            qty=qty,
            img=img,
            category=category
        )
        db.session.add(products)
        db.session.commit()
        return redirect('/')






@app.route('/<int:id>/edit',methods = ['GET','POST'])
def update(id):
    products = ProductModel.query.filter_by(id=id).first()

    #hobbies = student.hobbies.split(' ')
    # print(hobbies)
    if request.method == 'POST':
        if products:
            db.session.delete(products)
            db.session.commit()
    #     tv = request.form['tv']    
    #     if tv is None:
    #               pass

    #    # print('Form:' + str(request.form))    
      
    #     cricket = request.form['cricket']
    #     movies = request.form['movies']
    #     hobbies = tv + ' ' +  cricket + ' ' + movies
    #     print('H' + hobbies)
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            qty = request.form['qty']
            category = request.form['category']
            img = request.form['img']
            products = ProductModel(
                name=name,
                description=description,
                price=price,
                qty=qty,
                img=img,
                category=category
            )
        db.session.add(products)
        db.session.commit()
        return redirect('/')
        return f"Student with id = {id} Does nit exist"
 
    return render_template('editpage.html', products = products)












@app.route('/')
def RetrieveList():
    products = ProductModel.query.all()
    return render_template('listeproduit.html', products=products)


@app.route('/products', methods=['GET'])
def getAllProduct():
    products = ProductModel.query.all()
    result = products_schema.dump(products)
    return jsonify(result)


@app.route('/<int:id>/delete', methods=['GET', 'POST'])
def delete(id):
    products = ProductModel.query.filter_by(id=id).first()
    if request.method == 'POST':
        if products:
            db.session.delete(products)
            db.session.commit()
            return redirect('/')

    return render_template('delete.html')


if __name__ == '__main__':
    app.run(host='localhost', debug=True)
