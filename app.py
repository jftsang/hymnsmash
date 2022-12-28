import os

import dotenv
from flask import Flask, jsonify, render_template

from models import db, listdict, Competitor, Match

dotenv.load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI')

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index_view():
    return render_template('index.html')


@app.route('/competitor')
def competitor_list_view():  # put application's code here
    return jsonify(listdict(Competitor.query.all()))


@app.route('/match')
def match_list_view():
    return jsonify(listdict(Match.query.all()))


if __name__ == '__main__':
    app.run()
