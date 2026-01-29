from __future__ import annotations

from typing import Dict, Any

from .utils import ask_str, ask_int, ask_float, CustomerProfile, BusinessRuleError
from .offers import recommend_plan
from .prompts import build_message


class HyperPersonalizedAgent:
    def run(self) -> None:
        print("\n==============================")
        print("🤖 Agente: Mensajes Hiperpersonalizados")
        print("==============================\n")
        print(
            "Hola 👋 Soy tu agente de recomendaciones de plan.\n"
            "Te haré algunas preguntas rápidas y te diré el plan que mejor te conviene.\n"
        )

        try:
            profile = self.collect_profile()
            rec = recommend_plan(profile)
            messages = build_message(profile, rec["plan"], rec)
            self.print_summary(profile, rec, messages)

        except BusinessRuleError as e:
            print("\n❌ Error de negocio:")
            print(f"   {e}")

        except ValueError as e:
            print("\n❌ Error en los datos ingresados:")
            print(f"   {e}")

        except Exception as e:
            # En producción: logging
            print("\n🚨 Error inesperado del sistema")
            print("   Intenta nuevamente o revisa la configuración.")
            print(f"   Detalle técnico: {e}")

    # --------------------------------------------------
    # Validación + captura segura del perfil
    # --------------------------------------------------
    def collect_profile(self) -> CustomerProfile:
        try:
            name = ask_str("1) ¿Cómo te llamas? ")
            age = ask_int("2) ¿Qué edad tienes? ", min_v=10, max_v=90)
            city = ask_str("3) ¿En qué ciudad estás? ")

            data_gb = ask_float(
                "4) ¿Cuántos GB usas al mes (aprox)? ",
                min_v=0,
                max_v=500
            )

            minutes = ask_int(
                "5) ¿Cuántos minutos llamas al mes (aprox)? ",
                min_v=0,
                max_v=10000
            )

            sms = ask_int(
                "6) ¿Cuántos SMS envías al mes (aprox)? ",
                min_v=0,
                max_v=10000,
                default=0
            )

            heavy_social = ask_str(
                "7) ¿Usas MUCHO redes sociales? (si/no) ",
                default="si"
            ).lower().startswith("s")

            heavy_video = ask_str(
                "8) ¿Ves MUCHO video (TikTok/YouTube)? (si/no) ",
                default="si"
            ).lower().startswith("s")

            hotspot = ask_str(
                "9) ¿Compartes internet (hotspot) seguido? (si/no) ",
                default="no"
            ).lower().startswith("s")

            current_plan_usd = ask_float(
                "10) ¿Cuánto pagas hoy por tu plan ($/mes)? ",
                min_v=0,
                max_v=500,
                default=0
            )

            budget_usd = ask_float(
                "11) ¿Cuál es tu presupuesto ideal ($/mes)? ",
                min_v=0,
                max_v=500,
                default=current_plan_usd
            )

            pain_point = ask_str(
                "12) ¿Qué te molesta de tu plan actual? "
                "(ej: 'me quedo sin datos', 'pago de más') ",
                default="me quedo sin datos"
            )

        except Exception as e:
            raise ValueError(f"Entrada inválida: {e}")

        # Validación defensiva adicional
        if budget_usd <= 0:
            raise BusinessRuleError(
                "El presupuesto debe ser mayor a cero para recomendar un plan."
            )

        return CustomerProfile(
            name=name,
            age=age,
            city=city,
            data_gb=data_gb,
            minutes=minutes,
            sms=sms,
            heavy_social=heavy_social,
            heavy_video=heavy_video,
            hotspot=hotspot,
            current_plan_usd=current_plan_usd,
            budget_usd=budget_usd,
            pain_point=pain_point
        )

    # --------------------------------------------------
    # Salida segura en consola
    # --------------------------------------------------
    def print_summary(
        self,
        profile: CustomerProfile,
        rec: Dict[str, Any],
        messages: Dict[str, str]
    ) -> None:
        try:
            plan = rec["plan"]

            print("\n\n✅ PERFIL CAPTURADO")
            print(f"- Cliente: {profile.name} ({profile.age}) – {profile.city}")
            print(f"- Consumo: {profile.data_gb:.1f} GB | {profile.minutes} min | {profile.sms} SMS")
            print(
                f"- Preferencias: redes={'sí' if profile.heavy_social else 'no'} | "
                f"video={'sí' if profile.heavy_video else 'no'} | "
                f"hotspot={'sí' if profile.hotspot else 'no'}"
            )
            print(
                f"- Presupuesto: ${profile.budget_usd:.0f} | "
                f"Plan actual: ${profile.current_plan_usd:.0f}"
            )
            print(f"- Dolor: {profile.pain_point}")

            print("\n🎯 RECOMENDACIÓN")
            print(
                f"➡️ {plan.name} (${plan.price_usd:.0f}/mes) | "
                f"{plan.data_gb:.0f}GB, {plan.minutes} min"
            )

            print("Motivos:")
            for r in rec.get("reasons", [])[:5]:
                print(f"  - {r}")

            print("\n🧠 MENSAJES GENERADOS (para demo)\n")
            for k in ["formal", "whatsapp", "sms", "ahorro", "beneficios"]:
                if k in messages:
                    print("---------------------------------")
                    print(f"[{k.upper()}]\n{messages[k]}")

        except KeyError as e:
            raise BusinessRuleError(
                f"Falta información clave en la recomendación: {e}"
            )
