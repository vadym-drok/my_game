from app.models import Nation
from app.settings import (
    POPULATION_GROWTH_PERCENT,
    POPULATION_GROWTH_REQUIRED_HEALTHY_DAYS,
)


def population_growth_limit(population: int) -> int:
    return population * POPULATION_GROWTH_PERCENT // 100


def population_growth_available(nation: Nation) -> bool:
    return nation.population_growth_progress >= POPULATION_GROWTH_REQUIRED_HEALTHY_DAYS
