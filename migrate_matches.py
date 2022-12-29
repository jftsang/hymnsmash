from app import app
from models import db, Match

with app.app_context():
    matches = db.session.execute(db.select(Match)).scalars()
    for match in matches:
        if match.result is None:
            match.winner_id = match.player1_id
            match.loser_id = match.player2_id
            match.meh = True
        elif match.result is True:
            match.winner_id = match.player1_id
            match.loser_id = match.player2_id
            match.meh = False
        elif match.result is False:
            match.winner_id = match.player2_id
            match.loser_id = match.player1_id
            match.meh = False
        else:
            raise AssertionError

    db.session.commit()
