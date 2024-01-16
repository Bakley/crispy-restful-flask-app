from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)
api = Api(app)

# Model
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    
    def __init__(self, name) -> None:
        self.name = name
        
# View 
class UserResource(Resource):
    
    parser = reqparse.RequestParser()
    parser.add_argument("name", required=True, help="Name cannot be blank", type=str)
    
    def get(self):
        users = UserModel.query.all()
        user_data = [{
            "id": user.id,
            'name': user.name
        } for user in users]
        new_user = user_data
        return {"users": user_data}, 200
    
    def post(self):
        args = self.parser.parse_args()
        name = args.get("name")
        new_object = UserModel(name=name)
        
        try:
            db.session.add(new_object)
            db.session.commit()
            return {"user" :{
                'id': new_object.id,
                'name': new_object.name
            }}, 201
        except Exception as e:
            db.session.rollback()
            return {
                'error': str(e)
            }, 500
        finally:
            db.session.close()
 
      
class UserListResource(Resource):
    
    def get(self, id):
        response = UserModel.query.filter_by(id=id).first()
        if response:
            return {
                'id': response.id,
                'name': response.name
            }, 200
        return {
            'error': 'User not found'
        }, 404
    
    def put(self, id):
        user_query = UserModel.query.get(id)
        
        if not user_query:
            return {
                'error': "User not found"
            }, 404
        
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True, help="Name cannot be blank", type=str)
        args = parser.parse_args()
        user_query.name = args.get("name")
        
        try:
            db.session.commit()
            return {
                'id': user_query.id,
                'name': user_query.name
            }, 201
        except Exception as e:
            return {
                'error' : str(e)
            }, 500
        finally:
            db.session.close()

        

with app.app_context():
    db.create_all()

# Controller   
api.add_resource(UserResource, '/users')
api.add_resource(UserListResource, '/users/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
