from flask import Flask, jsonify, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from sqlalchemy import null

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
    children2 = db.relationship('Commande',backref='Client')
    

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
    children2 = db.relationship('DetailCommande',backref='ProductModel')

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
        
class Commande(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    id_Client=db.Column(db.Integer, db.ForeignKey(Client.id)) 
    dateComande=db.Column(db.String(100))
    adresseCommande =db.Column(db.String(100))
    TotalPrix=db.Column(db.Float) 
    status=db.Column(db.String(100))
    children = db.relationship('DetailCommande',backref='Commande')

    def _ini_(self,id_Client,dateComande,adresseCommande,TotalPrix,status):
        self.id_Client=id_Client
        self.dateComande=dateComande
        self.adresseCommande=adresseCommande
        self.TotalPrix=TotalPrix
        self.status=status

class DetailCommande(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    id_Comande=db.Column(db.Integer, db.ForeignKey(Commande.id)) 
    id_product=db.Column(db.Integer, db.ForeignKey(ProductModel.id)) 
    prix_unitaire=db.Column(db.Float)
    qty_unitaire=db.Column(db.Integer)

    def _ini_(self,id_Comande,id_product,prix_unitaire,qty_unitaire):
        self.id_Comande=id_Comande
        self.id_product=id_product
        self.prix_unitaire=prix_unitaire
        self.qty_unitaire=qty_unitaire
         

    

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

class CommandeSchema(ma.Schema):
    class Meta:
        fields = ('id','id_Client','TotalPrix','dateComande','adresseCommande','status')

class DetailCommandeSchema(ma.Schema):
    class Meta:
        fields = ('id','id_Comande','id_product','prix_unitaire','qty_unitaire')

# INIT SCHEMA
client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)

product_schema = ProductModelSchema()
products_schema = ProductModelSchema(many=True)

panier_schema = PanierSchema()
paniers_schema = PanierSchema(many=True)

commande_schema = CommandeSchema()
commandes_schema = CommandeSchema(many=True)


detailComande_schema = DetailCommandeSchema()
detailComandes_schema = DetailCommandeSchema(many=True)


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
    qte = request.json['qte']
    new_panier = Panier(id_Client=id_Client,id_Product=id_Product,qte=qte)
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
    requet = Panier.query.filter_by(id_Client=id).all()
    totalPrice = 0
    for i in requet:
        produit=ProductModel.query.filter_by(id=i.id_Product).first()
        totalPrice+=i.qte*produit.price
    return {'total':str(totalPrice)}  

@app.route('/getQte/<id>')  
def getQte(id):
    qte = Panier.query.filter_by(id_Client=id).all()
    nbrQte = 0
    for i in qte:
        nbrQte+=i.qte
    return {'total':str(nbrQte)}  

@app.route('/deleteProductFromPanier/<id>/<idp>',methods=['DELETE'])
def deleteProductFromPanier(id,idp):
    panier=Panier.query.filter_by(id_Client=id,id_Product=idp).first()
    db.session.delete(panier)
    db.session.commit()
    return {"results":'deleted'}

@app.route('/ajouteCommande',methods=['POST'])
def ajouterCommande():
    ## fields = ('id','id_Client','TotalPrix','dateComande','adresseCommande','status')
    id_Client = request.json['id_Client']
    TotalPrix = request.json['TotalPrix']
    dateComande = request.json['dateComande']
    adresseCommande = request.json['adresseCommande']
    status=request.json['status']
    new_commande = Commande(id_Client=id_Client,TotalPrix=TotalPrix,dateComande=dateComande,adresseCommande=adresseCommande,status=status)
    db.session.add(new_commande)
    db.session.commit()
    return {"results": str(new_commande.id)} 

@app.route('/ajouteDetailCommande',methods=['POST'])
def ajouteDetailCommande():
    ## fields = ('id','id_Client','TotalPrix','dateComande','adresseCommande','status')
    id_Comande = request.json['id_Comande']
    prix_unitaire = request.json['prix_unitaire']
    qty_unitaire = request.json['qty_unitaire']
    new_commande = DetailCommande(id_Comande=id_Comande,prix_unitaire=prix_unitaire,qty_unitaire=qty_unitaire)
    db.session.add(new_commande)
    db.session.commit()
    return {"results": "ok"} 

       


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
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            qty = request.form['qty']
            category = request.form['category']
            img = request.form['img']
            products.name=name
            products.description=description
            products.price=price
            products.qty=qty
            products.category=category
            products.img=img
        db.session.commit()
        return redirect('/')
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
