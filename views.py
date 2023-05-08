from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus

from flask import (
    jsonify,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    make_response,
    session,
    Response,
)
from markupsafe import Markup

from filters import leaderboard_color
from models import db, Competitor, Match, serialize_competitor_details


def index_view():
    if (cc := session.get('currentCompetition')) is not None:
        id1, id2 = cc
        p1 = db.get_or_404(Competitor, id1)
        p2 = db.get_or_404(Competitor, id2)
    else:
        p1, p2 = Competitor.pick_two()

    leaderboard = [(p1, 'table-success'), (p2, 'table-warning')]
    recent = [
        db.get_or_404(Competitor, cid)
        for cid in session.get('recentCompetitors', [])
    ]
    leaderboard += [(c, 'table-default') for c in recent if c not in {p1, p2}]

    resp = make_response(
        render_template('index.html', p1=p1, p2=p2, leaderboard=leaderboard)
    )
    session['currentCompetition'] = (p1.id, p2.id)
    return resp


def leaderboard_view():
    sortby = {
        'wins': Competitor.wins.desc(),
        'losses': Competitor.losses.desc(),
        'ladder': Competitor.ladder.desc(),
        'elo': Competitor.elo.desc(),
    }
    sortby_param = request.args.get('sortBy', 'elo')

    if sortby_param not in sortby:
        flash(f'Invalid sortBy parameter {sortby_param}')
        sortby_param = 'elo'

    competitors = db.session.execute(
        db.select(Competitor).order_by(sortby[sortby_param])
    ).scalars()

    leaderboard = [(c, leaderboard_color(c)) for c in competitors]

    return render_template('leaderboard.html', leaderboard=leaderboard)


def competitor_list_api_view():
    cids = request.args.get('cids', '')
    if cids:
        competitors = [
            db.get_or_404(Competitor, int(cid)) for cid in cids.split(',')
        ]
    else:
        competitors = db.session.execute(db.select(Competitor)).scalars()
    return jsonify([c.to_dict() for c in competitors])


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
    return render_template(
        'competitorDetails.html',
        c=c,
        details=serialize_competitor_details(c),
        results=results,
    )


def match_create_view():
    def formget(field):
        try:
            return request.form[field]
        except KeyError:
            return Response(status=HTTPStatus.BAD_REQUEST)

    submitter = formget('submitter')
    id1 = formget('p1')
    id2 = formget('p2')
    winner = formget('winner')

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
        delo_winner = -K * winner_e
        delo_loser = -K * loser_e
        winner.ladder = 0
        loser.ladder = 0
        winner.losses += 1
        loser.losses += 1
    else:
        delo_winner = K * (1 - winner_e)
        delo_loser = -K * loser_e
        winner.ladder += 1
        loser.ladder = 0
        winner.wins += 1
        loser.losses += 1

    winner.elo += delo_winner
    loser.elo += delo_loser

    match = Match(
        submitter=submitter,
        timestamp=datetime.now().timestamp(),
        winner_id=winner_id,
        loser_id=loser_id,
        delo_winner=delo_winner,
        delo_loser=delo_loser,
        meh=meh,
    )
    db.session.add(match)
    db.session.commit()

    resp = make_response(redirect(url_for('index_view')))
    session['currentCompetition'] = None

    # TODO use a deque (n.b. not JSON serializable) to have more than
    # two elements at a time - but beware dupes.
    session['recentCompetitors'] = [winner.id, loser.id]

    flash(
        Markup(
            f'<strong><a class="link text-decoration-none" href="/competitor/{winner.id}">{winner.name}</a></strong>: '
            f'<strong>{winner.elo}</strong> (<strong>{delo_winner:+.0f}</strong>)'
        )
    )
    flash(
        Markup(
            f'<strong><a class="link text-decoration-none" href="/competitor/{loser.id}">{loser.name}</a></strong>: '
            f'<strong>{loser.elo}</strong> (<strong>{delo_loser:+.0f}</strong>)'
        )
    )
    return resp
