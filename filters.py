from models import weight, metadata


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
