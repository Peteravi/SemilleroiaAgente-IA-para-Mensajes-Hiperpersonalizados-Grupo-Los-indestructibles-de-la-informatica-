from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# =========================
# ERRORES DE NEGOCIO
# =========================

class BusinessRuleError(Exception):
    """
    Error controlado para reglas de negocio.
    No es error técnico, es error de dominio.
    """
    pass


# =========================
# INPUTS CON VALIDACIÓN
# =========================

def ask_str(prompt: str, default: Optional[str] = None, min_len: int = 1) -> str:
    while True:
        raw = input(prompt).strip()
        if raw and len(raw) >= min_len:
            return raw
        if not raw and default is not None:
            return default
        print(f"⚠️ Ingresa un texto válido (mínimo {min_len} caracteres).")


def ask_int(
    prompt: str,
    min_v: int = 0,
    max_v: int = 10_000,
    default: Optional[int] = None
) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            val = int(raw)
            if val < min_v or val > max_v:
                raise BusinessRuleError(
                    f"Valor fuera de rango ({min_v} - {max_v})"
                )
            return val
        except ValueError:
            print("⚠️ Ingresa un número entero válido.")
        except BusinessRuleError as e:
            print(f"⚠️ {e}")


def ask_float(
    prompt: str,
    min_v: float = 0.0,
    max_v: float = 10_000.0,
    default: Optional[float] = None
) -> float:
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            val = float(raw)
            if val < min_v or val > max_v:
                raise BusinessRuleError(
                    f"Valor fuera de rango ({min_v} - {max_v})"
                )
            return val
        except ValueError:
            print("⚠️ Ingresa un número válido.")
        except BusinessRuleError as e:
            print(f"⚠️ {e}")


# =========================
# MODELO DE DOMINIO
# =========================

@dataclass
class CustomerProfile:
    name: str
    age: int
    city: str
    data_gb: float
    minutes: int
    sms: int
    heavy_social: bool
    heavy_video: bool
    hotspot: bool
    current_plan_usd: float
    budget_usd: float
    pain_point: str

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.name or len(self.name) < 2:
            raise BusinessRuleError("El nombre del cliente no es válido.")

        if self.age < 10 or self.age > 90:
            raise BusinessRuleError("Edad fuera de rango permitido.")

        if self.data_gb < 0 or self.data_gb > 500:
            raise BusinessRuleError("Consumo de datos inválido.")

        if self.minutes < 0 or self.sms < 0:
            raise BusinessRuleError("Minutos o SMS no pueden ser negativos.")

        if self.budget_usd < 0:
            raise BusinessRuleError("El presupuesto no puede ser negativo.")

        if self.current_plan_usd > 0 and self.budget_usd > 0:
            if self.budget_usd < self.current_plan_usd * 0.5:
                raise BusinessRuleError(
                    "El presupuesto es irreal comparado con el plan actual."
                )

        if not self.pain_point or len(self.pain_point) < 3:
            raise BusinessRuleError("El punto de dolor no está definido.")
