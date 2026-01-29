from __future__ import annotations

from typing import Dict, Any
from .offers import Plan
from .utils import CustomerProfile


def build_message(profile: CustomerProfile, plan: Plan, context: Dict[str, Any]) -> Dict[str, str]:
    reasons = context.get("reasons", [])
    price_delta = float(context.get("price_delta", 0.0))

    greeting = f"¡Hola {profile.name}! 👋" if profile.age <= 25 else f"Hola {profile.name},"

    if price_delta < 0:
        delta_txt = f"Y además pagarías aproximadamente ${abs(price_delta):.0f} menos al mes."
    elif price_delta > 0:
        delta_txt = f"Sube cerca de ${price_delta:.0f} vs tu plan actual, pero se alinea mejor a tu uso."
    else:
        delta_txt = "Mantienes un costo muy similar a tu plan actual."

    why = ", ".join(reasons[:3]) if reasons else "se ajusta a tu perfil"

    formal = (
        f"{greeting}\n"
        f"Según tu consumo (≈ {profile.data_gb:.1f} GB, {profile.minutes} min) y tu presupuesto (${profile.budget_usd:.0f}), "
        f"mi recomendación es: **{plan.name} (${plan.price_usd:.0f}/mes)**.\n"
        f"¿Por qué? Porque {why}.\n"
        f"{delta_txt}\n"
        f"Si te parece, puedo ayudarte a realizar el cambio de plan ahora mismo."
    )

    whatsapp = (
        f"{greeting} Vi tu consumo este mes 👀 (≈ {profile.data_gb:.1f}GB) y por eso te recomiendo **{plan.name}** por ${plan.price_usd:.0f}/mes.\n"
        f"✅ Motivo: {why}.\n"
        f"{delta_txt}\n"
        f"¿Te lo activo de una? Responde: *SI*"
    )

    sms = (
        f"{profile.name}: Recomendado {plan.name} (${plan.price_usd:.0f}/mes). "
        f"Cubre tu uso (~{profile.data_gb:.1f}GB). Responde SI para cambiar."
    )

    ahorro = (
        f"{greeting} Te propongo **{plan.name}** (${plan.price_usd:.0f}/mes).\n"
        f"En base a tu consumo, es la mejor relación costo/beneficio. {delta_txt}\n"
        f"¿Quieres que lo dejemos activo desde hoy?"
    )

    beneficios = (
        f"{greeting} Para que no vuelvas a sufrir por *{profile.pain_point}*, lo ideal es **{plan.name}**.\n"
        f"Incluye {plan.data_gb:.0f}GB, {plan.minutes} min y {('redes ilimitadas' if plan.social_unlimited else 'redes estándar')}.\n"
        f"¿Te hago el cambio ahora?"
    )

    return {
        "formal": formal,
        "whatsapp": whatsapp,
        "sms": sms,
        "ahorro": ahorro,
        "beneficios": beneficios,
    }
