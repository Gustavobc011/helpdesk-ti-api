from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return {"mensagem": "API do Helpdesk de TI - em construcao"}

if __name__ == "__main__":
    app.run(debug=True)