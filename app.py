import os

import dotenv
from flask import Flask

import filters
import views
from models import db, Competitor, metadata, weight

dotenv.load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI')

db.init_app(app)

with app.app_context():
    db.create_all()

filters.Filter.app_register(app)

app.route('/')(views.index_view)
app.route('/leaderboard')(views.leaderboard_view)
app.route('/competitor')(views.competitor_list_view)
app.route('/competitor/<cid>')(views.competitor_detail_view)
app.route('/match', methods=['POST'])(views.match_create_view)

if __name__ == '__main__':
    app.run()
