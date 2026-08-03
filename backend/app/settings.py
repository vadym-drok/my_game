"""Global game-balance settings."""

BASE_FOOD_SPENDING = 1
ACTIVE_POPULATION_PERCENT = 80
POPULATION_GROWTH_INTERVAL_DAYS = 5
POPULATION_GROWTH_PERCENT = 10


def active_population(population: int) -> int:
    return population * ACTIVE_POPULATION_PERCENT // 100
