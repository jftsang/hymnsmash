from app import app
from models import Competitor, db


def count_matches(c: Competitor) -> (int, int):
    won_matches, lost_matches = Competitor.get_matches(c)
    fake_victories = len([m for m in won_matches if m.meh])
    return len(won_matches) - fake_victories, len(
        lost_matches) + fake_victories


with app.app_context():
    competitors = db.session.execute(db.select(Competitor)).scalars()
    for c in competitors:
        wins, losses = count_matches(c)
        c.wins = wins
        c.losses = losses

    db.session.commit()
