import os
from flask import Flask
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from models import db
from auth import auth_bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from chamados import chamados_bp

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///helpdesk.db"
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")


db.init_app(app)
jwt = JWTManager(app)
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