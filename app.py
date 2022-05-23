from flask import Flask, jsonify, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import null
import os


# Définition de l'application "app"
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


# Définition de la base de données "db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialisation de la base de données "db"
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Définitions des classes
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    telephone = db.Column(db.String(300))
    password = db.Column(db.String)

    def __init__(self, pseudo, email, telephone, password):
        self.pseudo = pseudo
        self.email = email
        self.telephone = telephone
        self.password = password


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100), unique=True)
    mail = db.Column(db.String(100), unique=True)
    image = db.Column(db.String(300))
    numberPhone = db.Column(db.String(300))
    password = db.Column(db.String)
    children = db.relationship('Panier', backref='Client')
    children2 = db.relationship('Commande', backref='Client')

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
    children = db.relationship('Panier', backref='ProductModel')

    def _init_(self, name, description, price, qty, img, category):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty
        self.img = img
        self.category = category


class Panier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_Client = db.Column(db.Integer, db.ForeignKey(Client.id))
    id_Product = db.Column(db.Integer, db.ForeignKey(ProductModel.id))
    product_name = db.Column(db.Text)
    product_image = db.Column(db.Text)
    product_price = db.Column(db.Float)
    qte = db.Column(db.Integer)

    def _init_(self, id_Client, id_Product, product_name, product_image, product_price, qte):
        self.id_Client = id_Client
        self.id_Product = id_Product
        self.product_name = product_name
        self.product_image = product_image
        self.product_price = product_price
        self.qte = qte


class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_Client = db.Column(db.Integer, db.ForeignKey(Client.id))
    dateComande = db.Column(db.String(100))
    adresseCommande = db.Column(db.String(100))
    TotalPrix = db.Column(db.Float)
    liste_product = db.Column(db.Text)
    paiment_method = db.Column(db.String(100))
    status = db.Column(db.String(100))

    def _ini_(self, id_Client, dateComande, adresseCommande, TotalPrix, liste_product, paiment_method, status):
        self.id_Client = id_Client
        self.dateComande = dateComande
        self.adresseCommande = adresseCommande
        self.TotalPrix = TotalPrix
        self.liste_product = liste_product
        self.paiment_method = paiment_method
        self.status = status


# Création des schémas
class ClientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nickname', 'mail', 'image', 'numberPhone', 'password')


class ProductModelSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description',
                  'price', 'qty', 'img', 'category')


class PanierSchema(ma.Schema):
    class Meta:
        fields = ('id',
                  'id_Client',
                  'id_Product',
                  'product_name',
                  'product_image',
                  'product_price',
                  'qte')


class CommandeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_Client',
                  'dateComande', 'adresseCommande', 'TotalPrix', 'liste_product',
                  'paiment_method', 'status')


# Initialisation des schémas
client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)

product_schema = ProductModelSchema()
products_schema = ProductModelSchema(many=True)

panier_schema = PanierSchema()
paniers_schema = PanierSchema(many=True)

commande_schema = CommandeSchema()
commandes_schema = CommandeSchema(many=True)


# Définition des routes: MOBILE
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


@app.route('/products', methods=['GET'])
def getAllProduct():
    products = ProductModel.query.all()
    result = products_schema.dump(products)
    return jsonify(result)


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


@app.route('/ajoutePanier', methods=['POST'])
def ajouterPanier():
    id_Client = request.json['id_client']
    id_Product = request.json['id_product']
    product_name = request.json['product_name']
    product_image = request.json['product_image']
    product_price = request.json['product_price']
    qte = request.json['qte']
    new_panier = Panier(id_Client=id_Client, id_Product=id_Product, product_name=product_name,
                        product_image=product_image, product_price=product_price, qte=qte)
    db.session.add(new_panier)
    db.session.commit()
    return {"results": "ok"}


@app.route('/getPanierItems/<id>', methods=['GET'])
def getPanierItems(id):
    requet = Panier.query.filter_by(id_Client=id).all()
    rs = paniers_schema.dump(requet)
    return jsonify(rs)


@app.route('/getTotalPrix/<id>', methods=['GET'])
def getTotalPrixPanier(id):
    requet = Panier.query.filter_by(id_Client=id).all()
    totalPrice = 0
    for i in requet:
        produit = ProductModel.query.filter_by(id=i.id_Product).first()
        totalPrice += i.qte*produit.price
    return {'total': str(totalPrice)}


@app.route('/getQte/<id>')
def getQte(id):
    qte = Panier.query.filter_by(id_Client=id).all()
    nbrQte = 0
    for i in qte:
        nbrQte += i.qte
    return {'total': str(nbrQte)}


@app.route('/getPanierProductQte/<id>')
def getPanierProductQte(id):
    qte = Panier.query.filter_by(id_Client=id).all()
    panier = paniers_schema.dump(qte)
    return jsonify(panier)


@app.route('/deleteProductFromPanier/<id>/<idp>', methods=['DELETE'])
def deleteProductFromPanier(id, idp):
    panier = Panier.query.filter_by(id_Client=id, id_Product=idp).first()
    db.session.delete(panier)
    db.session.commit()
    return {"results": 'deleted'}


@app.route('/ajouteCommande', methods=['POST'])
def ajouterCommande():
    id_Client = request.json['id_Client']
    dateComande = request.json['dateComande']
    adresseCommande = request.json['adresseCommande']
    TotalPrix = request.json['TotalPrix']
    liste_product = request.json['liste_product']
    paiment_method = request.json['paiment_method']
    status = request.json['status']
    new_commande = Commande(id_Client=id_Client, dateComande=dateComande, adresseCommande=adresseCommande,
                            TotalPrix=TotalPrix, liste_product=liste_product, paiment_method=paiment_method, status=status)
    db.session.add(new_commande)
    db.session.commit()
    return {"results": str(new_commande.id)}


# Définition des routes: WEB
@app.route('/liste_produits')
def liste_produits():
    products = ProductModel.query.all()
    nbrCommandes = Commande.query.count()
    nbrCommandesConfirmees = Commande.query.filter_by(status="Accepted").count()
    nbrClients = Client.query.count()
    nbrProduits = ProductModel.query.count()
    return render_template('/liste_produits.html', products=products, nbrCommandes=nbrCommandes, nbrClients=nbrClients, nbrProduits=nbrProduits, nbrCommandesConfirmees=nbrCommandesConfirmees)


@app.route('/liste_commandes', methods=['GET'])
def liste_commandes():
    commandes = Commande.query.all()
    commandesFinalisees = Commande.query.filter_by(status="Accepted")
    revenue = 0.0
    for commande in commandesFinalisees:
        revenue += commande.TotalPrix
    return render_template('/liste_commandes.html', commandes=commandes, revenue=revenue)


@app.route('/liste_clients')
def liste_clients():
    clients = Client.query.all()
    return render_template('/liste_clients.html', clients=clients)    


@app.route('/page_ajout', methods=['GET', 'POST'])
def page_ajout():
    if request.method == 'GET':
        return render_template('page_ajout.html')
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
        return redirect('/liste_produits')


@app.route('/<int:id>/page_modification', methods=['GET', 'POST'])
def page_modification(id):
    products = ProductModel.query.filter_by(id=id).first()
    if request.method == 'POST':
        if products:
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            qty = request.form['qty']
            category = request.form['category']
            img = request.form['img']
            products.name = name
            products.description = description
            products.price = price
            products.qty = qty
            products.category = category
            products.img = img
        db.session.commit()
        return redirect('/liste_produits')
    return render_template('/page_modification.html', products=products)


@app.route('/<int:id>/supprimer_produit', methods=['GET', 'POST'])
def supprimer_produit(id):
    products = ProductModel.query.filter_by(id=id).first()
    if request.method == 'POST':
        if products:
            db.session.delete(products)
            db.session.commit()
            return redirect('/liste_produits')
    return render_template('/supprimer_produit.html')


@app.route('/<int:id>/supprimer_client', methods=['GET', 'POST'])
def supprimer_client(id):
    clients = Client.query.filter_by(id=id).first()
    if request.method == 'POST':
        if clients:
            db.session.delete(clients)
            db.session.commit()
            return redirect('/liste_clients')
    return render_template('/supprimer_client.html')


@app.route('/<int:id>/details_article', methods=['GET'])
def details_article(id):
    liste_commandes = Commande.query.all()
    commandes = []
    product = ProductModel.query.filter_by(id=id).first()
    for commande_a_chercher in liste_commandes:
        liste_prods = commande_a_chercher.liste_product.split("\n")
        for prod in liste_prods[:-1]:
            info_prod = prod.split(":")
            if id == int(info_prod[0]):
                commandes.append(Commande.query.filter_by(liste_product=commande_a_chercher.liste_product).first())
    if liste_commandes:
        return render_template('/details_article.html', commandes=commandes, product=product)
    else:
        return render_template('/details_article.html', product=product)


@app.route('/<int:id>/details_client', methods=['GET'])
def details_client(id):
    commandes = Commande.query.filter_by(id_Client=id)
    client = Client.query.filter_by(id=id).first()
    return render_template('/details_client.html', client=client, commandes=commandes)


@app.route('/<int:id>/accepter_commande', methods=['POST'])
def accepter_commande(id):
    commande = Commande.query.filter_by(id=id).first()
    commande.status = "Accepted"
    liste_prods = commande.liste_product.split("\n")
    for prod in liste_prods[:-1]:
        info_prod = prod.split(":")
        product = ProductModel.query.filter_by(id=int(info_prod[0])).first()
        product.qty -= int(info_prod[2])
    db.session.commit()
    return redirect('/liste_commandes')
    

@app.route('/<int:id>/refuser_commande', methods=['POST'])
def refuser_commande(id):
    commande = Commande.query.filter_by(id=id).first()
    status = "Rejected"
    commande.status = status
    db.session.commit()
    return redirect('/liste_commandes')


@app.route('/admin/inscription_admin', methods=['GET', 'POST'])
def inscription_admin():
    error = ""
    admins = Admin.query.all()
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        email = request.form['email']
        telephone = request.form['telephone']
        password = request.form['password']
        for admin in admins:
            if admin.email == email:
                error = "Cette adresse email est déja réservée! Réessayer"
                return render_template('/admin/inscription_admin.html', error=error)
        new_admin = Admin(pseudo=pseudo, email=email, telephone=telephone,
                            password=password)
        db.session.add(new_admin)
        db.session.commit()
        return redirect('/')
    return render_template('/admin/inscription_admin.html', error=error)


@app.route('/', methods=['GET', 'POST'])
def connexion_admin():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            if password == admin.password:
                return redirect('/liste_produits')
            else:
                error = "Mot de passe invalid! Réesayer"
        else:
            error = "Email introuvable! Réesayer"
    return render_template('/admin/connexion_admin.html', error=error)


# Initialisation de l'application "app"
if __name__ == '__main__':
    app.run(host='localhost', debug=True)
