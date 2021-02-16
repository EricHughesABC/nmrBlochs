# flask_code.py

from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/nmrBlochs")
def nmrBlochs():
    # this is a comment, just like in Python
    # note that the function name and the route argument
    # do not need to be the same.

    return render_template("index.html")

if __name__ == "__main__":
    print()
    app.run(debug=True)