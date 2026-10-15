import os
from flask import Flask
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from models import db
from auth import auth_bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from chamados import chamados_bp
from flasgger import Swagger

load_dotenv()

app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL", "sqlite:///helpdesk.db")

# Algumas hospedagens usam "postgres://", mas o SQLAlchemy exige "postgresql://"
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")


db.init_app(app)
jwt = JWTManager(app)
swagger_template = {
    "info": {
        "title": "API Helpdesk de TI",
        "description": "API REST para abertura e acompanhamento de chamados de suporte.",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Cole o token no formato: Bearer SEU_TOKEN"
        }
    }
}
swagger = Swagger(app, template=swagger_template)
app.register_blueprint(auth_bp)
app.register_blueprint(chamados_bp)


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return {"mensagem": "API do Helpdesk de TI - em construcao"}


@app.route("/perfil")
@jwt_required()
def perfil():
    usuario_id = get_jwt_identity()
    return {"mensagem": f"Voce esta autenticado como usuario de id {usuario_id}"}


if __name__ == "__main__":
    app.run(debug=True)