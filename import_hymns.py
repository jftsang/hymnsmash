import pandas as pd
from sqlalchemy.exc import IntegrityError

from app import app
from models import Competitor, db

df = pd.read_csv('neh.csv')
names = df['firstLine'] + ' (' + df['number'] + ')'

with app.app_context():
    for name in names:
        try:
            c = Competitor(name=name, elo=1500)
            db.session.add(c)
        except IntegrityError:
            continue

    db.session.commit()
