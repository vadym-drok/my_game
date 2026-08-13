from app.config import Settings
from app.population_growth import population_growth_available, population_growth_limit
from app.models import Nation


def test_population_growth_limit() -> None:
    assert population_growth_limit(9) == 1
    assert population_growth_limit(34) == 3
    assert population_growth_limit(35) == 4


def test_population_growth_requires_healthy_days() -> None:
    nation = Nation(name="Growth", population=50)
    assert not population_growth_available(nation)
    nation.population_growth_progress = 5
    assert population_growth_available(nation)


def test_settings_default_day_progress_mode() -> None:
    assert Settings(database_url="postgresql+psycopg://test:test@localhost/test").day_progress_mode == "reload"
