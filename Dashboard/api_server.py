from __future__ import annotations
import os
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from bot.bot_context import build_dashboard_context
from bot.bot_engine import answer_with_snapp_bot
from shared.snapp_data import (
    compute_latest_values,
    compute_opportunity_df,
    compute_signals_base,
    load_and_prepare_data,
)


BASE_DIR = Path(os.environ.get("SNAPP_BASE_DIR", Path(__file__).resolve().parents[1]))
CLEAN_DIR = Path(os.environ.get("SNAPP_CLEAN_DIR", BASE_DIR / "Clean_Data"))
STATIC_DIR = Path(__file__).parent / "bot_overlay_static"

app = FastAPI(title="Snapp Bot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnswerRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


def _build_context() -> dict[str, Any]:
    data = load_and_prepare_data(CLEAN_DIR)
    latest = compute_latest_values(data)

    base_signals = compute_signals_base(
        cpi=data["cpi"],
        fx=data["fx"],
        rates=data["rates"],
        esi=data["esi"],
        cpix=data["cpix"],
        trends=data["trends"],
    )
    opp = compute_opportunity_df(base_signals)
    top3 = opp.head(3)["Sector"].tolist() if (opp is not None and not opp.empty) else []

    return build_dashboard_context(
        latest_cpi=latest["latest_cpi"],
        latest_fx=latest["latest_fx"],
        latest_rates=latest["latest_rates"],
        latest_trends_date=latest["latest_trends_date"],
        latest_epra_cycle=latest["latest_epra_cycle"],
        latest_wb_year=latest["latest_wb_year"],
        latest_year=latest["latest_year"],
        acc_latest_year=latest["acc_latest_year"],
        latest_wb_reg_year=latest["latest_wb_reg_year"],
        esi=data["esi"],
        cpix=data["cpix"],
        kra_events=data["kra_events"],
        base_signals=base_signals,
        opportunity_df=opp,
        top3_opportunity=top3,
    )


app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/context")
def context():
    try:
        return _build_context()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/answer", response_model=AnswerResponse)
def answer(payload: AnswerRequest):
    question = (payload.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    ctx = _build_context()
    text = answer_with_snapp_bot(question, ctx)
    return AnswerResponse(answer=text)


@app.get("/")
def root():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"service": "snapp-bot-api"}

