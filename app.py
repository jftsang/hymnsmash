import os

import dotenv
from flask import Flask

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


@app.template_filter()
def format_elo(elo):
    return str(elo)


@app.template_filter()
def format_delo(delo: int | None) -> str:
    if delo is None:
        return ''
    return f'{delo:+d}'


@app.template_filter()
def hymn_number(competitor):
    return metadata(competitor).get('number', '')


@app.template_filter()
def hymnary_url(competitor):
    return f"https://hymnary.org/hymn/NEH/{hymn_number(competitor)}"


@app.template_filter()
def format_weight(competitor):
    return f'{weight(competitor):.2f}'


@app.template_filter()
def describe_winloss(competitor):
    wins, losses = competitor.wins, competitor.losses
    if wins + losses:
        perc = 100 * wins / (wins + losses)
    else:
        perc = 0
    return f'{wins} - {losses}<br/>({perc:.1f}%)'


app.route('/')(views.index_view)
app.route('/competitor')(views.competitor_list_view)
app.route('/competitor/<cid>')(views.competitor_detail_view)
app.route('/match', methods=['GET'])(views.match_list_view)
app.route('/match', methods=['POST'])(views.match_create_view)

if __name__ == '__main__':
    app.run()
