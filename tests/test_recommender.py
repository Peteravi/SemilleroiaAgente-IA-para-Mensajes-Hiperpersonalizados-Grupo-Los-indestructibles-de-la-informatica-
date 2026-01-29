from src.offers import get_plans, recommend_plan
from src.utils import CustomerProfile


def test_recommend_plan_basic():
    profile = CustomerProfile(
        name="Ana",
        age=22,
        city="Quito",
        data_gb=18.0,
        minutes=300,
        sms=10,
        heavy_social=True,
        heavy_video=True,
        hotspot=False,
        current_plan_usd=18.0,
        budget_usd=22.0,
        pain_point="me quedo sin datos"
    )
    rec = recommend_plan(profile)
    assert rec["plan"].name in [p.name for p in get_plans()]
