from flask import Flask
from flask_restful import Api
from db import db
from resources.user import UserRegister, UserLogin, UserLogout, User
from resources.token import TokenRefresh, CheckToken
from models.user import UserModel
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

app = Flask(__name__)
api = Api(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

###########################
### DB CONFIG
###########################

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/testdb'
app.config['SQLAlCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

### ACHTUNG
app.secret_key = 'matthias' # Das sollte nich öffentlich einsehbar sein
app.config['JWT_SECRET_KEY'] = 'matthias123'

###########################
### ADD CLAIMS TO JWT-TOKEN
###########################
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    user = UserModel.find_by_id(user)
    return {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_role': user.user_role
    }

###########################
### REST ENDPOINTS
###########################
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(CheckToken, "/checktoken")
api.add_resource(User, "/user/<int:user_id>")

###########################
### DB Initialisierung
###########################
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(host='0.0.0.0', debug=True)
