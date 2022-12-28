import os
from datetime import time, datetime
from http import HTTPStatus
from random import sample

import dotenv
from flask import Flask, jsonify, render_template, request, flash, redirect, \
    url_for

from models import db, listdict, Competitor, Match

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
    return f'{elo:.1f}'


@app.route('/')
def index_view():
    competitors = list(Competitor.all())
    p1, p2 = sample(competitors, k=2)
    return render_template('index.html', p1=p1, p2=p2, competitors=competitors)


@app.route('/competitor')
def competitor_list_view():
    results = Competitor.all()
    return jsonify(listdict(results))


@app.route('/match', methods=['GET', 'POST'])
def match_view():
    if request.method == 'POST':
        submitter = request.form['submitter']
        id1 = request.form['p1']
        c1 = db.get_or_404(Competitor, id1)
        id2 = request.form['p2']
        c2 = db.get_or_404(Competitor, id2)
        winner = request.form['winner']

        if winner not in {'1', '2'}:
            flash('Winner field not populated properly', 'error')
            return redirect(url_for('index_view'), HTTPStatus.BAD_REQUEST)

        q1 = 10 ** (c1.elo / 400)
        q2 = 10 ** (c2.elo / 400)
        e1 = q1 / (q1 + q2)
        e2 = q2 / (q1 + q2)
        K = 32

        if winner == '1':
            delo1 = K * (1 - e1)
            delo2 = K * (-1 - e2)
            result = True
        else:
            delo1 = K * (-1 - e1)
            delo2 = K * (1 - e2)
            result = False

        c1.elo += delo1
        c2.elo += delo2

        match = Match(submitter=submitter,
                      timestamp=datetime.now().timestamp(), player1_id=id1,
                      player2_id=id2,
                      result=result)
        db.session.add(match)
        db.session.commit()
        flash(f'{c1.name} score changed {delo1:.1f}')
        flash(f'{c2.name} score changed {delo2:.1f}')
        return redirect(url_for('index_view'))
    else:
        return jsonify(listdict(Match.query.all()))


if __name__ == '__main__':
    app.run()
