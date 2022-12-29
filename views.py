from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from random import choices

from flask import jsonify, render_template, request, flash, redirect, \
    url_for, make_response
from markupsafe import Markup

from models import db, listdict, Competitor, Match, weight, \
    serialize_competitor_details


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


def competitor_list_view():
    results = Competitor.all()
    return jsonify(listdict(results))


def competitor_detail_view(cid):
    @dataclass
    class MatchResultDescription:
        verb: str
        other: Competitor
        match: Match

    c = db.get_or_404(Competitor, cid)
    results = []
    matches1 = list(db.session.execute(
        db.select(Match).filter_by(player1_id=c.id)
    ).scalars())
    for match in matches1:
        other = db.get_or_404(Competitor, match.player2_id)
        if match.result is True:
            verb = "Won"
        elif match.result is False:
            verb = "Lost"
        elif match.result is None:
            verb = "Meh"
        else:
            raise AssertionError

        results.append(MatchResultDescription(verb, other, match))

    matches2 = list(db.session.execute(
        db.select(Match).filter_by(player2_id=c.id)
    ).scalars())
    for match in matches2:
        other = db.get_or_404(Competitor, match.player1_id)
        if match.result is False:
            verb = "Won"
        elif match.result is True:
            verb = "Lost"
        elif match.result is None:
            verb = "Meh"
        else:
            raise AssertionError

        results.append(MatchResultDescription(verb, other, match))

    results.sort(key=lambda r: r.match.timestamp)

    # return jsonify(serialize_competitor_details(c))
    # return jsonify(match_msgs)
    return render_template('competitorDetails.html', c=c,
                           details=serialize_competitor_details(c),
                           results=results)


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
            f'<strong><a class="link text-decoration-none" href="/competitor/{c1.id}">{c1.name}</a></strong>: '
            f'<strong>{c1.elo}</strong> (<strong>{delo1:+.0f}</strong>)'
        ))
        flash(Markup(
            f'<strong><a class="link text-decoration-none" href="/competitor/{c2.id}">{c2.name}</a></strong>: '
            f'<strong>{c2.elo}</strong> (<strong>{delo2:+.0f}</strong>)'
        ))
        return resp
    else:
        return jsonify(listdict(Match.query.all()))
