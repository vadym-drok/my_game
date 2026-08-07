from app.population_growth import population_growth_limit


assert population_growth_limit(9) == 1
assert population_growth_limit(34) == 3
assert population_growth_limit(35) == 4
