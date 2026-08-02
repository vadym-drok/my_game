"""Global game-balance settings."""

BASE_FOOD_SPENDING = 1
ACTIVE_POPULATION_PERCENT = 80


def active_population(population: int) -> int:
    return population * ACTIVE_POPULATION_PERCENT // 100
