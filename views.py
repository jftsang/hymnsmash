from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus

import numpy as np
from numpy.random import choice

from flask import jsonify, render_template, request, flash, redirect, \
    url_for, make_response, session
from markupsafe import Markup

from models import db, listdict, Competitor, Match, weight, \
    serialize_competitor_details


def index_view():
    competitors = list(Competitor.all())

    if (cc := session.get('currentCompetition')) is not None:
        id1, id2 = cc
        p1 = db.get_or_404(Competitor, id1)
        p2 = db.get_or_404(Competitor, id2)
    else:
        weights = np.array([weight(c) for c in competitors])
        weights /= sum(weights)
        p1, p2 = choice(competitors, size=2,
                        replace=False,
                        p=weights)

    resp = make_response(
        render_template('index.html', p1=p1, p2=p2, competitors=competitors)
    )
    session['currentCompetition'] = (p1.id, p2.id)
    return resp


def competitor_list_view():
    results = Competitor.all()
    return jsonify(listdict(results))


def competitor_detail_view(cid):
    @dataclass
    class MatchResultDescription:
        verb: str
        other: Competitor
        match: Match
        delo: int

    c = db.get_or_404(Competitor, cid)
    results = []
    won_matches, lost_matches = Competitor.get_matches(c)
    for m in won_matches:
        other = db.get_or_404(Competitor, m.loser_id)
        verb = 'Meh' if m.meh else 'Won'
        results.append(MatchResultDescription(verb, other, m, m.delo_winner))

    for m in lost_matches:
        other = db.get_or_404(Competitor, m.winner_id)
        verb = 'Meh' if m.meh else 'Lost'
        results.append(MatchResultDescription(verb, other, m, m.delo_loser))

    results.sort(key=lambda r: r.match.timestamp)

    # return jsonify(serialize_competitor_details(c))
    return render_template('competitorDetails.html', c=c,
                           details=serialize_competitor_details(c),
                           results=results)


def match_list_view():
    return jsonify(listdict(Match.query.all()))


def match_create_view():
    submitter = request.form['submitter']
    id1 = request.form['p1']
    id2 = request.form['p2']
    winner = request.form['winner']

    if winner == '1':
        winner_id = id1
        loser_id = id2
        meh = False
    elif winner == '2':
        winner_id = id2
        loser_id = id1
        meh = False
    elif winner == 'skip':
        winner_id = id1
        loser_id = id2
        meh = True
        flash('You didn\'t like either of them? Sorry to hear that...')
    else:
        flash('Winner field not populated properly', 'error')
        return redirect(url_for('index_view'), HTTPStatus.BAD_REQUEST)

    winner = db.get_or_404(Competitor, winner_id)
    loser = db.get_or_404(Competitor, loser_id)

    winner_q = 10 ** (winner.elo / 400)
    loser_q = 10 ** (loser.elo / 400)
    winner_e = winner_q / (winner_q + loser_q)
    loser_e = loser_q / (winner_q + loser_q)
    K = 32

    if meh:
        delo_winner = - K * winner_e
        delo_loser = - K * loser_e
        winner.ladder = 0
        loser.ladder = 0
        winner.losses += 1
        loser.losses += 1
    else:
        delo_winner = K * (1 - winner_e)
        delo_loser = - K * loser_e
        winner.ladder += 1
        loser.ladder = 0
        winner.wins += 1
        loser.losses += 1

    winner.elo += delo_winner
    loser.elo += delo_loser

    match = Match(submitter=submitter,
                  timestamp=datetime.now().timestamp(),
                  winner_id=winner_id,
                  loser_id=loser_id,
                  delo_winner=delo_winner,
                  delo_loser=delo_loser,
                  meh=meh)
    db.session.add(match)
    db.session.commit()

    resp = make_response(redirect(url_for('index_view')))
    session['currentCompetition'] = None

    flash(Markup(
        f'<strong><a class="link text-decoration-none" href="/competitor/{winner.id}">{winner.name}</a></strong>: '
        f'<strong>{winner.elo}</strong> (<strong>{delo_winner:+.0f}</strong>)'
    ))
    flash(Markup(
        f'<strong><a class="link text-decoration-none" href="/competitor/{loser.id}">{loser.name}</a></strong>: '
        f'<strong>{loser.elo}</strong> (<strong>{delo_loser:+.0f}</strong>)'
    ))
    return resp
