import json

import pandas as pd
from sqlalchemy.exc import IntegrityError

from app import app
from models import Competitor, db

url = 'https://hymnary.org/instances?qu=hymnalNumber%3Aneh1985%20in%3Ainstances&sort=displayTitle&order=asc&export=csv&limit=10000'
df = pd.read_csv(url)

for row in df.itertuples():
    # print(row)
    c = Competitor(
        name=row.displayTitle,
        elo=1500,
        extra=json.dumps({'number': row.number}),
    )
    try:
        with app.app_context():
            db.session.add(c)
            db.session.commit()
            print(f'Saved {c.name}')
    except IntegrityError as exc:
        print(f'Ignored {c.name}: {exc}')
        continue
