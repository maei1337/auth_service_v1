from flask_restful import Resource
from models.token import TokenModel
from flask_jwt_extended import (create_access_token,
                                jwt_refresh_token_required,
                                get_jwt_identity,
                                get_jwt_claims,
                                jwt_required,
                                get_raw_jwt
                                )
from models.token import add_token_to_database
from flask import current_app as app

class CheckToken(Resource):
    @jwt_required
    def get(self):
        jti = get_raw_jwt()['jti']
        try:
            token = TokenModel.query.filter_by(jti=jti).one()
            return {'message': token.revoked}, 200
        except NoResultFound:
            return {'message': True}, 401


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        if current_user is None:
            return {'message': 'please provide valid refresh token'}, 400
        new_token = create_access_token(identity=current_user, fresh=False)
        try:
            add_token_to_database(new_token, app.config['JWT_IDENTITY_CLAIM'])
            return {'access_token': new_token}, 201
        except:
            return {'message': 'An error occured while token refresh'}, 500
