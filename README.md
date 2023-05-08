# HymnSmash

J. M. F. Tsang

---

Tinder for Hymns.

[Deployment on Heroku](https://hymnsmash.herokuapp.com/)

Data courtesy of [Hymnary.org](https://hymnary.org/).

## Running

1. Update `.env` to specify your database location and your secret key.
2. `pip install -r requirements.txt`
3.
    1. Run development server: `flask run`
    2. Production server: Something like `gunicorn -w 4 app:app`
