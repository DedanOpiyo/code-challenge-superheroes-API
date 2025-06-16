# server/app.py
#!/usr/bin/env python3
from api_exception import APIException
from flask import jsonify

from flask import Flask, make_response, request
from flask_migrate import Migrate
from werkzeug.exceptions import NotFound

from models import db, Hero, Power, HeroPower

# Flask application object
app = Flask(__name__)

# Configuration string for database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///superheroes.db'

# Disabling modification tracking to use less memory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creating Migrate object to manage schemas modifications
migrate = Migrate(app, db)

# Initializing the Flask application to use the database
db.init_app(app)


# Routes & Views
@app.route('/')
def index():
    response_body = f'''
        <h1>Home of Super Heroes</h1>
        <h3>This is the root path of super heroes app.</h3>
    '''
    headers = {}
    return make_response(response_body, 200, headers)

@app.route('/heroes', methods=['GET'])
def heroes():
    if request.method == 'GET':
        heroes = Hero.query.all()
        if not heroes:
            raise APIException("No heroes added yet. Please add one first.")
        heroes = [hero.to_dict(rules=('-hero_powers',)) for hero in heroes]
        return make_response(heroes, 200)

@app.route('/heroes/<int:id>', methods=['GET', 'DELETE'])
def hero_by_id(id):
    hero = Hero.query.get(id)
    if not hero:
        raise NotFound("Hero not found") # Hardcode: return jsonify({"error": "Hero not found"}), 404
    else:
        if request.method == 'GET':
            hero_dict = hero.to_dict(rules=('-hero_powers.hero',))
            return make_response(hero_dict, 200)
        
        elif request.method == 'DELETE':
            db.session.delete(hero)
            db.session.commit()
            
            response_body = {
                "delete_successful": True,
                "message": "Hero deleted."
            }
            response = make_response(
                response_body,
                200
            )
            return response

@app.route('/powers', methods=['GET'])
def powers():
    if request.method == 'GET':
        powers = Power.query.all()
        if not powers:
            raise APIException("No powers added yet. Please add one first.")
        powers = [hero.to_dict(rules=('-hero_powers',)) for hero in powers]
        return make_response(powers, 200)

@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def power_by_id(id):
    
    power = Power.query.get(id)
    
    if not power:
        raise NotFound("Power not found") # Error
    
    else:
        if request.method == 'GET':
            power_dict = power.to_dict(rules=('-power_heroes.power',))
            return make_response(power_dict, 200)

        elif request.method == 'PATCH':
            data = request.get_json()
            if not data:
                return jsonify({"error": "No update field provided."}), 404
            for attr in data:
                try:
                    setattr(power, attr, data[attr])
                except:
                    return jsonify({"errors": ["validation errors"]}), 422
            db.session.commit()
            data_dict = power.to_dict()
            return make_response(data_dict, 200)

@app.route('/hero_powers', methods=['POST'])
def post_hero_power():
        if request.method == 'POST':
            
            data = request.get_json()
            
            if not data:
                raise APIException( # Tell client what fields to specify/format their JSON
                    ["'strength' is rquired", "'hero_id is required", "'power_id is required"], 
                    status_code=404, 
                    payload={"missing_fields": {"strength": None, "hero_id": None, "power_id": None}}
                )
            else:
                try:
                    new_hero_power = HeroPower(
                        strength=data["strength"],
                        hero_id=data["hero_id"],
                        power_id=data["power_id"]
                    )
                    
                    db.session.add(new_hero_power)
                    db.session.commit()
                
                except ValueError: # Errors from custom validation (e.g., wrong strength value)
                    raise APIException("validation errors", status_code=422)
                
                except KeyError:
                    raise APIException("Missing required field", status_code=400)
                
                except: # Default. Any other exception is raised
                    raise APIException("validation errors", status_code=422)

                
                return make_response(new_hero_power.to_dict(rules=('-hero.hero_powers', '-power.power_heroes',)), 201)

# Error handlers
@app.errorhandler(NotFound)
def handle_not_found(e):
    description = e.description.strip() or "Not Found: The requested resource does not exist."
    return make_response({"error": description}, 404)

@app.errorhandler(APIException)
def handle_api_exception(e):
    return make_response(jsonify(e.to_dict()), e.status_code)

if __name__ == '__main__':
    app.run(port=5555, debug=True)