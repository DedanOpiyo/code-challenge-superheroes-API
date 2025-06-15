# server/models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    # serialize_rules = ('-hero_powers.hero', '-powers.heroes',) # serializer rules 
    serialize_only = ('id', 'name', 'super_name', 'hero_powers', )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # Relationships
    hero_powers = db.relationship('HeroPower', back_populates='hero')
    
    # Association proxy to get powers of this hero through hero_powers
    powers = association_proxy('hero_powers', 'power', 
                               creator=lambda power_obj: HeroPower(power=power_obj))
    
    # Validations
    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError("A hero must have a name.")
        return value

    @validates('super_name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError("A hero must have a super_name.")
        return value

    def __repr__(self):
        return f"Hero id={self.id}, name={self.name}, super_name={self.super_name}"
    
class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    # serialize_rules = ('-hero_powers.power', 'heroes.powers',) 
    serialize_only = ('id', 'name', 'description', )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Relationships
    power_heros = db.relationship('HeroPower', back_populates='power')

    # Association proxy to get heroes of this power through hero_powers
    heroes = association_proxy('hero_powers', 'hero', 
                               creator=lambda hero_obj: HeroPower(hero=hero_obj))
    
    # Validations
    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError("A hero must have a name.")
        return value
    
    @validates('description')
    def validate_description(self, key, value):
        if not value or len(value) < 20:
            raise ValueError('Power description should be at leas 20 characters long.')
        return value
    
    def __repr__(self):
        return f"Power id={self.id}, name={self.name}, description={self.description}"
    
class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    serialize_rules = ('-hero.hero_powers', '-power.hero_powers', '-hero.powers', '-power.heroes',) # This is a tupple

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String(8), nullable=False)
    # Foreign Keys
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    # Relationships
    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='power_heros')
    
    # Validations
    @validates('strength')
    def validate_strength(self, key, value):
        if value not in ['Strong', 'Weak', 'Average']:
            raise ValueError("HeroPower strength must be either: 'Strong', 'Weak' or 'Average'.")
        return value
    
    @validates('hero_id')
    def validate_hero_id(self, key, value):
        if not isinstance(value, int):
            raise ValueError("HeroPower hero_id must be a valid integer.")
        return value

    @validates('power_id')
    def validate_power_id(self, key, value):
        
        if not isinstance(value, int):
            raise ValueError("HeroPower power_id must be an integer.")
        return value

    def __repr__(self):
        return f"HeroPower id={self.id}, strength={self.strength}, hero_id={self.hero_id}, power_id={self.power_id}"