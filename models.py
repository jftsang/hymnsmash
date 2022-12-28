import json
from typing import TypeVar

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

T = TypeVar('T')


def listdict(xs: [T]) -> [dict]:
    return [x.to_dict() for x in xs]


class Competitor(db.Model):
    __tablename__ = 'competitor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    elo = db.Column(db.Integer, default=1500, nullable=False)
    ladder = db.Column(db.Integer, default=0, nullable=False)
    extra = db.Column(db.JSON)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'ladder': self.ladder,
            'elo': self.elo,
        }

    @classmethod
    def all(cls):
        return db.session.execute(
            db.select(cls)
            .order_by(cls.elo.desc())
        ).scalars()

    @staticmethod
    def count_matches(c: 'Competitor') -> (int, int):
        matches1 = list(db.session.execute(
            db.select(Match).filter_by(player1_id=c.id)
        ).scalars())
        matches2 = list(db.session.execute(
            db.select(Match).filter_by(player2_id=c.id)
        ).scalars())

        wins = (
            len([m for m in matches1 if m.result is True])
            + len([m for m in matches2 if m.result is False])
        )
        losses = (
            len([m for m in matches1 if m.result is False])
            + len([m for m in matches2 if m.result is True])
        )
        return wins, losses


class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    submitter = db.Column(db.String, nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('competitor.id'))
    # player1 = db.relationship("Competitor")
    player2_id = db.Column(db.Integer, db.ForeignKey('competitor.id'))
    # player2 = db.relationship("Competitor")
    result = db.Column(db.Boolean, nullable=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'submitter': self.submitter,
            'player1_id': self.player1_id,
            'player2_id': self.player2_id,
            'result': self.result,
        }


def metadata(c: Competitor) -> dict:
    return json.loads(c.extra or '{}')


def weight(c: Competitor) -> float:
    return max(((c.elo - 1200) / 100) ** 2, 1)


def serialize_competitor_details(c: Competitor) -> dict:
    d = c.to_dict()
    d['weight'] = weight(c)

    d['matches'] = ([match.id for match in matches1]
                    + [match.id for match in matches2])

    wins, losses = count_matches(c)

    d['wins'] = wins
    d['losses'] = losses

    return d
