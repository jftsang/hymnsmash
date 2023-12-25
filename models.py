import json
from math import exp
from typing import TypeVar

import numpy as np
from flask_sqlalchemy import SQLAlchemy
from numpy.random import choice

from utils import BinomialDistribution

db = SQLAlchemy()

T = TypeVar('T')


def listdict(xs: [T]) -> [dict]:
    return [x.to_dict() for x in xs]


class Competitor(db.Model):
    __tablename__ = 'competitor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    elo = db.Column(db.Integer, default=1500, nullable=False)
    wins = db.Column(db.Integer, default=0, nullable=False)
    losses = db.Column(db.Integer, default=0, nullable=False)
    ladder = db.Column(db.Integer, default=0, nullable=False)
    extra = db.Column(db.JSON)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'ladder': self.ladder,
            'elo': self.elo,
            'wins': self.wins,
            'losses': self.losses,
            'extra': json.loads(self.extra),
        }

    @classmethod
    def all(cls):
        return db.session.execute(
            db.select(cls).order_by(cls.elo.desc())
        ).scalars()

    @staticmethod
    def get_matches(c: 'Competitor') -> (['Match'], ['Match']):
        won_matches = list(
            db.session.execute(
                db.select(Match).filter_by(winner_id=c.id)
            ).scalars()
        )
        lost_matches = list(
            db.session.execute(
                db.select(Match).filter_by(loser_id=c.id)
            ).scalars()
        )
        return won_matches, lost_matches

    @classmethod
    def pick_two(cls) -> ('Competitor', 'Competitor'):
        competitors = list(cls.all())
        weights = np.array([weight(c) for c in competitors])
        weights /= sum(weights)
        p1 = None
        p2 = None
        delo = float('inf')
        while delo > 200:
            p1, p2 = choice(competitors, size=2, replace=False, p=weights)
            delo = abs(p1.elo - p2.elo)

        return p1, p2


class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    submitter = db.Column(db.String, nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('competitor.id'))
    loser_id = db.Column(db.Integer, db.ForeignKey('competitor.id'))
    delo_winner = db.Column(db.Integer, nullable=True)
    delo_loser = db.Column(db.Integer, nullable=True)
    meh = db.Column(db.Boolean, nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'submitter': self.submitter,
            'winner_id': self.winner_id,
            'loser_id': self.loser_id,
            'delo_winner': self.delo_winner,
            'delo_loser': self.delo_loser,
            'meh': self.meh,
        }


def metadata(c: Competitor) -> dict:
    return json.loads(c.extra or '{}')


def weight(c: Competitor) -> float:
    if n := c.wins + c.losses:
        _, uncertainty = BinomialDistribution.estimate_p(n, c.wins)
    else:
        uncertainty = 1
    return 2 / (1 + exp(-(c.elo - 1500) / 100)) * (1 + uncertainty)


def serialize_competitor_details(c: Competitor) -> dict:
    d = c.to_dict()
    d['weight'] = weight(c)

    won_matches, lost_matches = Competitor.get_matches(c)

    matches = sorted(won_matches + lost_matches, key=lambda m: m.timestamp)

    d['matches'] = [match.id for match in matches]
    wins, losses = len(won_matches), len(lost_matches)
    d['wins'] = wins
    d['losses'] = losses

    return d
