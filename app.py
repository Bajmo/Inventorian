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
    children = db.relationship('Panier',backref='Client')

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
    children = db.relationship('Panier',backref='ProductModel')

    def _init_(self, name, description, price, qty, img, category):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty
        self.img = img
        self.category = category

class Panier(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    id_Client=db.Column(db.Integer, db.ForeignKey(Client.id)) 
    id_Product=db.Column(db.Integer, db.ForeignKey(ProductModel.id)) 
    qte=db.Column(db.Integer)

    def _init_(self,id_Client,id_Product,qte):
        self.id_Client=id_Client
        self.id_Product=id_Product
        self.qte=qte
        
        
# SCHEMA


class ClientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nickname', 'mail', 'image', 'numberPhone', 'password')


class ProductModelSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description',
                  'price', 'qty', 'img', 'category')

class PanierSchema(ma.Schema):
    class Meta:
        fields = ('id','id_Client','id_Product','qte')

# INIT SCHEMA
client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)

product_schema = ProductModelSchema()
products_schema = ProductModelSchema(many=True)

panier_schema = PanierSchema()
paniers_schema = PanierSchema(many=True)


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

 

@app.route('/ajoutePanier',methods=['POST'])
def ajouterPanier():
    id_Client = request.json['id_client']
    id_Product = request.json['id_product']
    new_panier = Panier(id_Client=id_Client,id_Product=id_Product)
    db.session.add(new_panier)
    db.session.commit()
    return {"results": "ok"}

@app.route('/getProduitFromPanier/<id>',methods=['GET'])
def getProduitFromPanier(id):
    requet=ProductModel.query.join(Panier).filter_by(id_Client=id).all()
    rs=products_schema.dump(requet)
    return jsonify(rs)

@app.route('/getTotalPrix/<id>',methods=['GET'])
def getTotalPrixPanier(id):
    requet = ProductModel.query.join(Panier).filter_by(id_Client=id).all()
    totalPrice = 0
    for i in requet:
        totalPrice+=i.price*i.qty
    return {'total':str(totalPrice)}    

@app.route('/deleteProductFromPanier/<id>',methods=['DELETE'])
def deleteProductFromPanier(id):
    panier = Panier.query.get(id)
    db.session.delete(panier)
    db.session.commit()
    return {"results":'deleted'}


    




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

  
    if request.method == 'POST':
        if products:
            db.session.delete(products)
            db.session.commit()

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
    nbrClints = Client.query.count()
    nbrProduits = ProductModel.query.count()
    return render_template('listeproduit.html', products=products,nbrClints=nbrClints,nbrProduits=nbrProduits)



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
    app.run(host='192.168.1.117', debug=True)
