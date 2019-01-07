from flask_restful import Resource, reqparse
from models.user import UserModel
from models.token import TokenModel
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_refresh_token_required,
                                get_jwt_identity,
                                get_jwt_claims,
                                jwt_required,
                                get_raw_jwt
                                )
from models.token import add_token_to_database
from flask import current_app as app

###########################
### DELETE/LIST/UPDATE Single User
###########################
class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': 'User not found'}, 404

        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        try:
            if not user:
                return {'message': 'User with ID: {} not found'.format(user_id)}, 404
            user.delete_from_db()
            return {'message': 'User deleted'}, 200
        except:
            {'message': 'Error occured while deleting User'}, 500

    @jwt_required
    def put(cls, user_id):

        user_to_change = UserModel.find_by_id(user_id)
        #try:
        if not user_to_change:
            return {'message': 'User with ID: {} not found'.format(user_id)}, 404

        id = get_jwt_identity()
        user = get_jwt_claims()

        if id == user_to_change.id:
            return {"message": user["user_role"]}
        return {"message": 'falsch'}



        #except:
            #{'message': 'Error occured while updating User'}, 500


###########################
### Register a User
###########################
class UserRegister(Resource):
    def post(self):
        user_parser = reqparse.RequestParser()
        user_parser.add_argument('email', type=str, required=True, help="This field not left blank")
        user_parser.add_argument('password', type=str, required=True, help="This field not left blank")
        user_parser.add_argument('first_name', type=str, required=True, help="This field not left blank")
        user_parser.add_argument('last_name', type=str, required=True, help="This field not left blank")

        data = user_parser.parse_args()

        if UserModel.find_by_email(data['email']):

            return {'message': 'A user with that email already exist'}, 400
        try:
            user = UserModel(**data) # data['username'], data['password'], ...
            user.save_to_db()
        except:
            {'message': 'Error occured while Registration'}, 500

        return user.json(), 201


###########################
### Login a User and access/refresh token
###########################
class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_parser = reqparse.RequestParser()
        user_parser.add_argument('email', type=str, required=True, help="This field not left blank")
        user_parser.add_argument('password', type=str, required=True, help="This field not left blank")

        data = user_parser.parse_args()

        user = UserModel.find_by_email(data['email'])

        '''
        Check if the USER is accepted_user
        '''
        if user.accepted_user == True:
            if user and user.check_password(data['password']):
                try:
                    # Create ACCESS and REFRESH token
                    access_token = create_access_token(identity=user.id, fresh=True)
                    refresh_token = create_refresh_token(user.id)

                    # STORE TOKEN IN TOKENDB
                    add_token_to_database(access_token, app.config['JWT_IDENTITY_CLAIM'])
                    add_token_to_database(refresh_token, app.config['JWT_IDENTITY_CLAIM'])
                except:
                    return {'message': 'Error occured while login'}, 500

            return {'access_token': access_token, 'refresh_token': refresh_token}, 200

            return {'message': 'Invalid credentials'}, 401

        return {'message': 'Account not yet activated'}, 401


#### TEST USER_CLAIMS
    @jwt_required
    def get(self):
        id = get_jwt_identity()
        user = get_jwt_claims()
        return {'id': id, 'claims': user}


###########################
### Logout a User and set revoked token = True
###########################
class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti'] # JWT ID, a unique identifier for a JWT
        user_identity = get_jwt_identity()
        try:
            token = TokenModel.query.filter_by(jti=jti).one()
            token.revoked = True
            token.save_to_db()
            return {'message': 'Successfully logged out'}, 200
        except:
            return {'message': 'Token not found'}, 500
