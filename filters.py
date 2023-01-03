from markupsafe import Markup

from models import weight, metadata, Competitor
from utils import BinomialDistribution


class Filter:
    filters = []

    @classmethod
    def register(cls, f):
        cls.filters.append(f)
        return f

    @classmethod
    def app_register(cls, app):
        for f in cls.filters:
            app.template_filter()(f)


@Filter.register
def format_elo(elo):
    return str(elo)


@Filter.register
def format_delo(delo: int | None) -> str:
    if delo is None:
        return ''
    return f'{delo:+d}'


@Filter.register
def hymn_number(competitor):
    return metadata(competitor).get('number', '')


@Filter.register
def hymnary_url(competitor):
    return f"https://hymnary.org/hymn/NEH/{hymn_number(competitor)}"


@Filter.register
def format_weight(competitor):
    return f'{weight(competitor):.2f}'


@Filter.register
def winloss_perc(competitor):
    wins, losses = competitor.wins, competitor.losses
    # if n := (wins + losses):
    #     phat, error = BinomialDistribution.estimate_p(n, wins, z=1.96)
    #     return Markup(f'{phat * 100:.1f}% &#177; {error * 100:.1f}%')
    # else:
    #     return '&mdash;'
    if wins + losses:
        perc = 100 * wins / (wins + losses)
    else:
        perc = 0
    return f'{perc:.1f}%'


@Filter.register
def describe_winloss(competitor):
    wins, losses = competitor.wins, competitor.losses
    if wins + losses:
        perc = 100 * wins / (wins + losses)
    else:
        perc = 0
    return f'{wins} - {losses}<br/>({perc:.1f}%)'


@Filter.register
def p_estimate(competitor):
    wins, losses = competitor.wins, competitor.losses
    if wins + losses:
        phat, error = BinomialDistribution.estimate_p(wins + losses, wins)
        return Markup(
            f'{phat * 100:.1f}&nbsp;&#177;&nbsp;{error * 100:.1f}&nbsp;&percnt;'
        )

    return '&mdash;'


@Filter.register
def leaderboard_color(c: Competitor) -> str:
    if c.wins + c.losses:
        perc = 100 * c.wins / (c.wins + c.losses)
    else:
        return 'table-secondary'

    if perc >= 90:
        return 'table-success'
    elif perc <= 10:
        return 'table-danger'
    else:
        return 'table-default'
