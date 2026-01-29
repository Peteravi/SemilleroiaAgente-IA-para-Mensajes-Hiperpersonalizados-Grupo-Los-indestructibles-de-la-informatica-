from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from .utils import CustomerProfile, BusinessRuleError


# ======================================================
# MODELO DE PLAN (INMUTABLE)
# ======================================================

@dataclass(frozen=True)
class Plan:
    code: str
    name: str
    price_usd: float
    data_gb: float
    minutes: int
    sms: int
    social_unlimited: bool = False
    video_bonus_gb: float = 0.0
    hotspot_gb: float = 0.0


# ======================================================
# CATÁLOGO DE PLANES
# ======================================================

def get_plans() -> List[Plan]:
    plans = [
        Plan(code="P1", name="Plan Esencial", price_usd=10, data_gb=6, minutes=200, sms=200),
        Plan(code="P2", name="Plan Social", price_usd=15, data_gb=12, minutes=400, sms=400, social_unlimited=True),
        Plan(code="P3", name="Plan Video", price_usd=20, data_gb=20, minutes=600, sms=600, video_bonus_gb=10),
        Plan(code="P4", name="Plan Power", price_usd=25, data_gb=30, minutes=900, sms=900, social_unlimited=True, hotspot_gb=10),
        Plan(code="P5", name="Plan Pro Max", price_usd=35, data_gb=60, minutes=2000, sms=2000, social_unlimited=True, video_bonus_gb=20, hotspot_gb=25),
    ]

    if not plans:
        raise BusinessRuleError("No hay planes disponibles para recomendar.")

    return plans


# ======================================================
# SCORING DEFENSIVO
# ======================================================

def score_plan(profile: CustomerProfile, plan: Plan) -> float:
    if profile is None:
        raise ValueError("Perfil del cliente inválido.")

    if plan is None:
        raise ValueError("Plan inválido.")

    score = 0.0

    # --------------------------
    # Presupuesto
    # --------------------------
    if profile.budget_usd <= 0:
        raise BusinessRuleError("El presupuesto del cliente debe ser mayor a cero.")

    if plan.price_usd <= profile.budget_usd:
        score += 3.0
    else:
        score -= 5.0

    # --------------------------
    # Datos
    # --------------------------
    if plan.data_gb >= profile.data_gb:
        score += 3.0
    else:
        score -= (profile.data_gb - plan.data_gb) * 0.4

    # --------------------------
    # Minutos y SMS
    # --------------------------
    score += 1.0 if plan.minutes >= profile.minutes else -0.5
    score += 0.5 if plan.sms >= profile.sms else -0.25

    # --------------------------
    # Preferencias
    # --------------------------
    if profile.heavy_social and plan.social_unlimited:
        score += 2.0

    if profile.heavy_video and plan.video_bonus_gb > 0:
        score += 1.5

    if profile.hotspot and plan.hotspot_gb > 0:
        score += 1.0

    if profile.hotspot and plan.hotspot_gb == 0:
        score -= 0.8

    # --------------------------
    # Dolor del cliente
    # --------------------------
    pain = (profile.pain_point or "").lower()

    if "sin datos" in pain or "datos" in pain:
        score += 1.0 if plan.data_gb >= profile.data_gb else -1.0

    if "paga" in pain and ("mas" in pain or "más" in pain):
        score += 0.7 if plan.price_usd <= profile.current_plan_usd else -0.7

    return score


# ======================================================
# RECOMENDACIÓN FINAL (PROTEGIDA)
# ======================================================

def recommend_plan(profile: CustomerProfile) -> Dict[str, Any]:
    if profile is None:
        raise ValueError("No se recibió un perfil válido.")

    plans = get_plans()

    ranked = sorted(
        plans,
        key=lambda p: score_plan(profile, p),
        reverse=True
    )

    if not ranked:
        raise BusinessRuleError("No se pudo generar una recomendación.")

    best = ranked[0]

    # --------------------------
    # Explicabilidad
    # --------------------------
    reasons: List[str] = []

    if best.price_usd <= profile.budget_usd:
        reasons.append(f"se ajusta a tu presupuesto (${profile.budget_usd:.0f})")
    else:
        reasons.append("es el que más se acerca a tu consumo, aunque excede tu presupuesto")

    if best.data_gb >= profile.data_gb:
        reasons.append(f"cubre tus {profile.data_gb:.1f} GB/mes")
    else:
        reasons.append(f"te mejora los datos (tú usas {profile.data_gb:.1f} GB)")

    if profile.heavy_social and best.social_unlimited:
        reasons.append("incluye redes ilimitadas")

    if profile.heavy_video and best.video_bonus_gb > 0:
        reasons.append(f"incluye bono para video (+{best.video_bonus_gb:.0f} GB)")

    if profile.hotspot and best.hotspot_gb > 0:
        reasons.append(f"tiene hotspot incluido ({best.hotspot_gb:.0f} GB)")

    delta = best.price_usd - profile.current_plan_usd

    return {
        "plan": best,
        "reasons": reasons,
        "ranked": ranked,
        "price_delta": delta
    }
