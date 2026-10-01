from flask import Flask
from models import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///helpdesk.db"

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return {"mensagem": "API do Helpdesk de TI - em construcao"}

if __name__ == "__main__":
    app.run(debug=True)