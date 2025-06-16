#!/usr/bin/env python3
# server/seed.py

from app import app
from models import db, Hero, Power, HeroPower
from faker import Faker
from random import choice

with app.app_context():

    faker = Faker()

    # Delete all rows in our tables
    Hero.query.delete()
    Power.query.delete()
    HeroPower.query.delete()
    
    # # Comment out db.drop_all() and use it to test ERROR HANDLING/EXCEPTIONS (in app.py - routes)
    # db.drop_all() # If you uncoment this, comment .query.delete() above
    # db.create_all()

    # 1. Hero table
    for _ in range(10):
        hero = Hero(
            name=faker.name(),
            super_name=faker.city_suffix()
        )

        db.session.add(hero)
    db.session.commit()

    # 2. Power table
    powers = []
    for _ in range(10):
        power = Power(name=faker.color_name(), description=faker.catch_phrase())
        powers.append(power)
    
    db.session.add_all(powers)
    db.session.commit()

    # 3. HeroPower table
    heroes = Hero.query.all()
    powers = Power.query.all()
    
    strengths = ['Strong', 'Weak', 'Average']
    
    for _ in range(30):

        hero = choice(heroes)
        power = choice(powers)

        hp = HeroPower(
            strength=choice(strengths), 
            hero_id=hero.id, 
            power_id=power.id
        )
        
        db.session.add(hp)
    
    db.session.commit()