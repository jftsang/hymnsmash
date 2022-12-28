from typing import TypeVar

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

T = TypeVar('T')


def listdict(xs: [T]) -> [dict]:
    return [x.to_dict() for x in xs]


class Competitor(db.Model):
    __tablename__ = 'competitor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    elo = db.Column(db.Integer, default=1500)

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
