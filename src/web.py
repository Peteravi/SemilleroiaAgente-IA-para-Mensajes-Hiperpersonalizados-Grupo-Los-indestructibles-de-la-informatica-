from __future__ import annotations
from pathlib import Path
from typing import Literal
from datetime import datetime, date

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ValidationError

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, DateTime, func
)
from sqlalchemy.orm import declarative_base, sessionmaker

from .utils import CustomerProfile, BusinessRuleError
from .offers import recommend_plan
from .prompts import build_message


# ======================================================
# APP
# ======================================================

app = FastAPI(title="Agente Mensajes Hiperpersonalizados")

BASE_DIR = Path(__file__).resolve().parent

# Configurar templates - ruta CORRECTA: src/templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Configurar archivos estáticos - ruta CORRECTA: src/static
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)


# ======================================================
# DATABASE (SQLITE)
# ======================================================

DATABASE_URL = "sqlite:///./data/app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


# ======================================================
# DB MODELS
# ======================================================

class RecommendationDB(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    name = Column(String(50))
    city = Column(String(50))

    plan_name = Column(String(50))
    plan_price = Column(Float)
    budget = Column(Float)

    match_percent = Column(Integer)
    risk = Column(String(10))


class MetricsDailyDB(Base):
    __tablename__ = "metrics_daily"

    id = Column(Integer, primary_key=True)
    day = Column(Date, unique=True)

    total_requests = Column(Integer, default=0)
    avg_match = Column(Float, default=0.0)


# ======================================================
# INIT DB & STARTUP DEBUG
# ======================================================

@app.on_event("startup")
def startup_tasks():
    """Tareas de inicio: crear tablas y mostrar información de depuración"""
    # 1. Crear tablas de la base de datos
    Base.metadata.create_all(bind=engine)
    
    # 2. Mostrar información de depuración de rutas
    print("\n" + "="*50)
    print("INFORMACIÓN DE DEPURACIÓN DE RUTAS")
    print("="*50)
    
    # Verificar ruta de static
    static_path = BASE_DIR / "static"
    print(f"\n📁 Ruta static: {static_path}")
    print(f"   Existe: {static_path.exists()}")
    if static_path.exists():
        print(f"   Archivos en static: {list(static_path.glob('*'))}")
        # Verificar CSS específicos
        css_files = list(static_path.glob("*.css"))
        print(f"   Archivos CSS encontrados: {[f.name for f in css_files]}")
    
    # Verificar ruta de templates
    templates_path = BASE_DIR / "templates"
    print(f"\n📁 Ruta templates: {templates_path}")
    print(f"   Existe: {templates_path.exists()}")
    if templates_path.exists():
        print(f"   Archivos HTML encontrados: {list(templates_path.glob('*.html'))}")
    
    print("\n🌐 URLs disponibles para testing:")
    print(f"   - Estilos CSS: http://localhost:8002/static/dashboard.css")
    print(f"   - Dashboard: http://localhost:8002/dashboard")
    print(f"   - Página principal: http://localhost:8002/")
    print("="*50 + "\n")


# ======================================================
# ERROR HANDLER
# ======================================================

@app.exception_handler(BusinessRuleError)
async def business_rule_exception_handler(request: Request, exc: BusinessRuleError):
    return JSONResponse(
        status_code=400,
        content={"error": "Regla de negocio", "detail": str(exc)},
    )


# ======================================================
# INPUT MODEL
# ======================================================

class CustomerInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=12, le=100)
    city: str = Field(..., min_length=1, max_length=50)

    data_gb: float = Field(..., ge=0, le=500)
    minutes: int = Field(..., ge=0, le=50_000)
    sms: int = Field(0, ge=0, le=50_000)

    heavy_social: Literal["si", "no"] = "no"
    heavy_video: Literal["si", "no"] = "no"
    hotspot: Literal["si", "no"] = "no"

    current_plan_usd: float = Field(0, ge=0, le=1_000)
    budget_usd: float = Field(..., ge=0, le=1_000)

    pain_point: str = Field("me quedo sin datos", max_length=200)


# ======================================================
# ROUTES
# ======================================================

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/recomendar", response_class=HTMLResponse)
def recomendar(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    city: str = Form(...),
    data_gb: float = Form(...),
    minutes: int = Form(...),
    sms: int = Form(0),
    heavy_social: str = Form("no"),
    heavy_video: str = Form("no"),
    hotspot: str = Form("no"),
    current_plan_usd: float = Form(0),
    budget_usd: float = Form(...),
    pain_point: str = Form("me quedo sin datos"),
):

    # ----------------------
    # VALIDACIÓN
    # ----------------------
    try:
        validated = CustomerInput(
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
            pain_point=pain_point,
        )
    except ValidationError:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Datos inválidos. Revisa el formulario."}
        )

    # ----------------------
    # DOMAIN PROFILE
    # ----------------------
    profile = CustomerProfile(
        name=validated.name,
        age=validated.age,
        city=validated.city,
        data_gb=validated.data_gb,
        minutes=validated.minutes,
        sms=validated.sms,
        heavy_social=(validated.heavy_social == "si"),
        heavy_video=(validated.heavy_video == "si"),
        hotspot=(validated.hotspot == "si"),
        current_plan_usd=validated.current_plan_usd,
        budget_usd=validated.budget_usd,
        pain_point=validated.pain_point,
    )

    # ----------------------
    # BUSINESS LOGIC
    # ----------------------
    rec = recommend_plan(profile)
    plan = rec["plan"]
    messages = build_message(profile, plan, rec)

    savings_usd = profile.current_plan_usd - plan.price_usd
    match_percent = int(rec.get("match_percent", 85))
    risk = rec.get("risk", "Medio")

    ui = {
        "savings_usd": savings_usd,
        "match_percent": match_percent,
        "risk": risk,
    }

    # ----------------------
    # DATABASE
    # ----------------------
    db = SessionLocal()
    try:
        db.add(
            RecommendationDB(
                name=profile.name,
                city=profile.city,
                plan_name=plan.name,
                plan_price=plan.price_usd,
                budget=profile.budget_usd,
                match_percent=match_percent,
                risk=risk,
            )
        )

        today = date.today()
        metric = db.query(MetricsDailyDB).filter_by(day=today).first()

        if not metric:
            metric = MetricsDailyDB(
                day=today,
                total_requests=1,
                avg_match=match_percent
            )
            db.add(metric)
        else:
            metric.avg_match = (
                (metric.avg_match * metric.total_requests + match_percent)
                / (metric.total_requests + 1)
            )
            metric.total_requests += 1

        db.commit()

        history = (
            db.query(RecommendationDB)
            .order_by(RecommendationDB.created_at.desc())
            .limit(5)
            .all()
        )

    except Exception:
        db.rollback()
        history = []
    finally:
        db.close()

    # ----------------------
    # RESPONSE
    # ----------------------
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "profile": profile,
            "plan": plan,
            "messages": messages,
            "ui": ui,
            "history": history,
        },
    )


# ======================================================
# DASHBOARD
# ======================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/metrics")
def api_metrics():
    db = SessionLocal()
    try:
        total_recommendations = db.query(RecommendationDB).count()

        avg_match = (
            db.query(func.avg(RecommendationDB.match_percent))
            .scalar()
        ) or 0

        plans = (
            db.query(
                RecommendationDB.plan_name,
                func.count(RecommendationDB.id)
            )
            .group_by(RecommendationDB.plan_name)
            .all()
        )

        plans_data = [
            {"plan": p[0], "total": p[1]}
            for p in plans
        ]

        risk = (
            db.query(
                RecommendationDB.risk,
                func.count(RecommendationDB.id)
            )
            .group_by(RecommendationDB.risk)
            .order_by(func.count(RecommendationDB.id).desc())
            .first()
        )

        most_common_risk = risk[0] if risk else "N/A"

        daily = (
            db.query(MetricsDailyDB)
            .order_by(MetricsDailyDB.day.desc())
            .limit(7)
            .all()
        )

        daily_data = [
            {
                "day": d.day.isoformat(),
                "total_requests": d.total_requests,
                "avg_match": round(d.avg_match, 2)
            }
            for d in daily
        ]

        return {
            "total_recommendations": total_recommendations,
            "avg_match_percent": round(avg_match, 2),
            "most_common_risk": most_common_risk,
            "plans": plans_data,
            "daily_metrics": daily_data
        }

    finally:
        db.close()


# ======================================================
# API JSON
# ======================================================

@app.post("/api/recommend")
def api_recommend(payload: CustomerInput):
    profile = CustomerProfile(
        name=payload.name,
        age=payload.age,
        city=payload.city,
        data_gb=payload.data_gb,
        minutes=payload.minutes,
        sms=payload.sms,
        heavy_social=(payload.heavy_social == "si"),
        heavy_video=(payload.heavy_video == "si"),
        hotspot=(payload.hotspot == "si"),
        current_plan_usd=payload.current_plan_usd,
        budget_usd=payload.budget_usd,
        pain_point=payload.pain_point,
    )

    rec = recommend_plan(profile)
    plan = rec["plan"]
    messages = build_message(profile, plan, rec)

    return {
        "plan": plan.__dict__,
        "messages": messages,
    }