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
            'elo': self.elo,
        }

    @classmethod
    def all(cls):
        return db.session.execute(
            db.select(cls)
            .order_by(cls.elo.desc())
        ).scalars()


class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    submitter = db.Column(db.String, nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('competitor.id'))
    # player1 = db.relationship("Competitor")
    player2_id = db.Column(db.Integer, db.ForeignKey('competitor.id'))
    # player2 = db.relationship("Competitor")
    result = db.Column(db.Boolean, nullable=False)

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
    return d
