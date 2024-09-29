from extensions import db
from sqlalchemy import String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

# Define models (tables)
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # PK
    username = db.Column(String, unique=True, nullable=False)  # Name from Google signIn
    email = db.Column(String, unique=True, nullable=False)  # email from Google signIn
    isadmin = db.Column(db.Boolean, default=False)  # Admin authorization 

    def __repr__(self): 
        return f'<User {self.username}>'

class AdminEmails(db.Model):
    __tablename__ = 'admin_emails'
    id = db.Column(db.Integer, primary_key=True)  # PK
    email = db.Column(String, unique=True, nullable=False)  # Admin email

    def __repr__(self):
        return f'<AdminEmail {self.email}>'

class Categories(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)  # PK
    name = db.Column(String, nullable=False, unique=True)  # Category name

    def __repr__(self):
        return f'<Category {self.name}>'

class Addresses(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)  # PK
    merchant_id = db.Column(db.Integer, ForeignKey('merchants.id'), nullable=False)  # FK to Merchants
    address = db.Column(String, nullable=False)  # Address

    def __repr__(self):
        return f'<Address {self.address}>'
    
class RequestsMerchants(db.Model):
    __tablename__ = 'requests_merchants'
    id = db.Column(db.Integer, primary_key=True)  # PK
    name = db.Column(String, nullable=False)  # Merchant name
    category = db.Column(Enum('F&B', 'LifeStyle', name='category_enum'), nullable=False)  # Category with limited values
    contact_no = db.Column(String, nullable=False)  # Contact number
    requester_email = db.Column(String, nullable=False)  # Email

    def __repr__(self):
        return f'<RequestMerchant {self.name}>'

class Merchants(db.Model):
    __tablename__ = 'merchants'
    
    id = db.Column(db.Integer, primary_key=True)  # PK
    name = db.Column(String, nullable=False)  # Merchant name
    category_id = db.Column(db.Integer, ForeignKey('categories.id'), nullable=False)  # FK to Categories
    discount = db.Column(Text, nullable=False)  # Multiline string for discount
    more_info = db.Column(Text, nullable=True)  # Multiline string for additional info
    terms = db.Column(Text, nullable=False)  # Multiline string for terms

    category = relationship('Categories', backref='merchants')
    addresses = relationship('Addresses', backref='merchant', cascade='all, delete-orphan')
    images = relationship('MerchantImages', backref='merchant', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Merchant {self.name}>'

class MerchantImages(db.Model):
    __tablename__ = 'merchant_images'
    
    id = db.Column(db.Integer, primary_key=True)  # PK
    merchant_id = db.Column(db.Integer, ForeignKey('merchants.id'), nullable=False)  # FK to Merchants
    image_url = db.Column(String, nullable=True)  # Image URL, can be NULL

    def __repr__(self):
        return f'<MerchantImage {self.image_url}>'