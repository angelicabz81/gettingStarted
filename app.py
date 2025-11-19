from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask i love boba!!"

# in app.py
# python3 -m flask --app app --debug run
if __name__ == "__main__":
    app.run(debug=True)