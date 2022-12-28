import os
from datetime import time, datetime
from http import HTTPStatus
from random import sample, choices

import dotenv
from flask import Flask, jsonify, render_template, request, flash, redirect, \
    url_for, make_response
from markupsafe import Markup

from models import db, listdict, Competitor, Match, metadata, weight, \
    serialize_competitor_details

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


@app.template_filter()
def hymn_number(competitor):
    return metadata(competitor).get('number', '')


@app.template_filter()
def format_weight(competitor):
    return f'{weight(competitor):.2f}'


@app.template_filter()
def count_wins(competitor):
    wins, _ = Competitor.count_matches(competitor)
    return str(wins)


@app.template_filter()
def count_losses(competitor):
    _, losses = Competitor.count_matches(competitor)
    return str(losses)


@app.template_filter()
def describe_winloss(competitor):
    wins, losses = Competitor.count_matches(competitor)
    if wins + losses:
        perc = 100 * wins / (wins + losses)
    else:
        perc = 0
    return f'{wins} - {losses}<br/>({perc:.1f}%)'


@app.route('/')
def index_view():
    competitors = list(Competitor.all())

    if (
        cookie_content := request.cookies.get(
            'currentCompetition')) is not None:
        id1, id2 = cookie_content.split()
        p1 = db.get_or_404(Competitor, id1)
        p2 = db.get_or_404(Competitor, id2)
    else:
        p1, p2 = choices(competitors, k=2,
                         weights=[weight(c) for c in competitors])

    resp = make_response(
        render_template('index.html', p1=p1, p2=p2, competitors=competitors)
    )
    resp.set_cookie('currentCompetition', f'{p1.id} {p2.id}')
    return resp


@app.route('/competitor')
def competitor_list_view():
    results = Competitor.all()
    return jsonify(listdict(results))


@app.route('/competitor/<cid>')
def competitor_detail_view(cid):
    c = db.get_or_404(Competitor, cid)
    return jsonify(serialize_competitor_details(c))


@app.route('/match', methods=['GET', 'POST'])
def match_view():
    if request.method == 'POST':
        submitter = request.form['submitter']
        id1 = request.form['p1']
        c1 = db.get_or_404(Competitor, id1)
        id2 = request.form['p2']
        c2 = db.get_or_404(Competitor, id2)
        winner = request.form['winner']

        q1 = 10 ** (c1.elo / 400)
        q2 = 10 ** (c2.elo / 400)
        e1 = q1 / (q1 + q2)
        e2 = q2 / (q1 + q2)
        K = 32

        if winner == '1':
            delo1 = K * (1 - e1)
            delo2 = - K * e2
            c1.ladder += 1
            c2.ladder = 0
            result = True
        elif winner == '2':
            delo1 = - K * e1
            delo2 = K * (1 - e2)
            c1.ladder = 0
            c2.ladder += 1
            result = False
        elif winner == 'skip':
            delo1 = - K * e1
            delo2 = - K * e2
            c1.ladder = 0
            c2.ladder = 0
            result = None
            flash('You didn\'t like either of them? Sorry to hear that...')
        else:
            flash('Winner field not populated properly', 'error')
            return redirect(url_for('index_view'), HTTPStatus.BAD_REQUEST)

        c1.elo += delo1
        c2.elo += delo2

        match = Match(submitter=submitter,
                      timestamp=datetime.now().timestamp(), player1_id=id1,
                      player2_id=id2,
                      result=result)
        db.session.add(match)
        db.session.commit()

        resp = make_response(redirect(url_for('index_view')))
        resp.delete_cookie('currentCompetition')

        flash(Markup(
            f'<strong>{c1.name}</strong> score changed <strong>{delo1:.1f}</strong>'))
        flash(Markup(
            f'<strong>{c2.name}</strong> score changed <strong>{delo2:.1f}</strong>'))
        return resp
    else:
        return jsonify(listdict(Match.query.all()))


if __name__ == '__main__':
    app.run()
