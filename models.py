from extensions import db
from sqlalchemy import String, Text, ForeignKey, event
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from geoalchemy2 import Geography  # For spatial data

# Define models (tables)
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # PK
    username = db.Column(String, unique=True, nullable=False)  # Name from Google signIn
    email = db.Column(String, unique=True, nullable=False)  # email from Google signIn
    isadmin = db.Column(db.Boolean, default=False)  # Admin authorization 

    def __repr__(self): 
        return f'<User {self.username}>'

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
    address = db.Column(db.String, nullable=False)  # Address

    def __repr__(self):
        return f'<Address {self.address}>'

class Locations(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)  # PK
    merchant_id = db.Column(db.Integer, ForeignKey('merchants.id'), nullable=False)  # FK to Merchants
    location = db.Column(Geography(geometry_type='POINT', srid=4326), nullable=False, index=False)  # Location

    def __repr__(self):
        return f'<Location {self.location}>'

class Merchants(db.Model):
    __tablename__ = 'merchants'
    id = db.Column(db.Integer, primary_key=True)  # PK
    name = db.Column(String, nullable=False)  # Merchant name
    category_id = db.Column(db.Integer, ForeignKey('categories.id'), nullable=False)  # FK to Categories
    discount = db.Column(Text, nullable=False)  # Multiline string for discount
    more_info = db.Column(Text, nullable=True)  # Multiline string for additional info
    terms = db.Column(Text, nullable=False)  # Multiline string for terms
    image = db.Column(String, nullable=True)  # URL to the image

    category = relationship('Categories', backref='merchants')
    addresses = relationship('Addresses', backref='merchant', cascade='all, delete-orphan')
    locations = relationship('Locations', backref='merchant', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Merchant {self.name}>'

# Event listener to check the number of merchants in a category before deleting a merchant
@event.listens_for(Session, 'before_flush')
def check_and_delete_category(session, flush_context, instances):
    for instance in session.deleted:
        if isinstance(instance, Merchants):
            category = instance.category
            if len(category.merchants) == 1:
                session.delete(category)