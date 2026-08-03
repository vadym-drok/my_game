from datetime import date

from app.models import Nation
from app.settings import POPULATION_GROWTH_INTERVAL_DAYS, POPULATION_GROWTH_PERCENT


def population_growth_limit(population: int) -> int:
    return population * POPULATION_GROWTH_PERCENT // 100


def population_growth_available(nation: Nation, today: date | None = None) -> bool:
    today = today or date.today()
    last_growth_date = nation.last_population_growth_date or nation.start_date
    return (today - last_growth_date).days >= POPULATION_GROWTH_INTERVAL_DAYS
