import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drink():
    try:
        print('>>> starting')
        drinks = Drink.query.order_by(Drink.id).all()
        print('GET >>> drinks:', drinks)
        print('>>> step 2')
        result = [drink.short() for drink in drinks]
        print('>>> result' , result)
        if len(result) == 0:
            abort(404) # Not found - when there are no drink
        return jsonify({'success': True, 'drinks': result})
    except:
        abort(422) 

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_detailed_drink(*args, **kwargs):
    try:
        print('>>> starting')
        drinks = Drink.query.order_by(Drink.id).all()
        print('>>> drinks:', drinks)
        print('>>> step 2')
        result = [drink.long() for drink in drinks]
        print('1>>',type(result), result)
        
        if len(result) == 0:
            abort(404) # Not found - when there are no drink
        return jsonify({'success': True, 'drinks': result})
    except AuthError:
        abort(422) 


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
        
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(*args, **kwargs):
    body = request.get_json()
    new_title = body.get('title', None)
    #new_recipe="""{}""".format(body['recipe'],None)
    new_recipe = body.get('recipe', None)
    print('POST >>>>', new_title, new_recipe)
    try:
        #TEST FOR IF ITS NOT AN ARRAY TYPE 
        if type(new_recipe).__name__ != 'list':
            new_recipe = [new_recipe]
        new_recipe = json.dumps(new_recipe)
        new_drink = Drink(title=new_title, recipe=new_recipe) 
        new_drink.insert()
        drinkResults = Drink.query.get(new_drink.id)
        return jsonify({
        'success': True,
        'drinks': drinkResults.long()
        }, 200)
    except AuthError:
        abort(422)
          
        
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(*args, **kwargs):
    drink_id =kwargs.get('drink_id', None)
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    try:
       
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)
        if new_title is not None:
            drink.title = new_title
        if new_recipe is not None:
             #TEST FOR IF ITS NOT AN ARRAY TYPE 
            if type(new_recipe).__name__ != 'list':
                new_recipe = [new_recipe]
            drink.recipe = json.dumps(new_recipe)
            
        drink.update()
        drinkResults = [Drink.query.get(drink.id).long()]
        print('2>>',type(drinkResults), drinkResults)
        return jsonify({'success': True, 'drinks': drinkResults})
    except AuthError:
        abort(422)
    

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(*args, **kwargs):
    try:
        drink_id =kwargs.get('drink_id', None)
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({'success': True, 'deleted': drink.id})
    except AuthError: 
        abort(422)
    

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

'''
#* DONE  
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
#* DONE  
@DONE -  implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
        }), 400
  

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
