"""
KikuLog — FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.persistence import init_db
from app.routers import notes, houses, agenda, evaluation

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting KikuLog")
    await init_db()
    yield
    logger.info("Shutting down KikuLog")


app = FastAPI(
    title="KikuLog",
    description="Work journal and schedule assistant for chrysanthemum farm workers.",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")
templates = Jinja2Templates(directory="app/ui/templates")

# --- Routers ---
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(houses.router, prefix="/api/houses", tags=["houses"])
app.include_router(agenda.router, prefix="/api/agenda", tags=["agenda"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])


# --- Health check ---
@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "version": app.version}


# --- UI routes ---
@app.get("/", response_class=HTMLResponse, tags=["ui"])
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/journal", response_class=HTMLResponse, tags=["ui"])
async def journal(request: Request):
    return templates.TemplateResponse(request=request, name="journal.html")


@app.get("/agenda", response_class=HTMLResponse, tags=["ui"])
async def agenda_page(request: Request):
    return templates.TemplateResponse(request=request, name="agenda.html")


@app.get("/evaluation", response_class=HTMLResponse, tags=["ui"])
async def evaluation_page(request: Request):
    return templates.TemplateResponse(request=request, name="evaluation.html")
