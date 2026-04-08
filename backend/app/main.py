"""GTalk Backend — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes import auth, dashboard, transcriptions, tts, views

app = FastAPI(
    title="GTalk API",
    description=(
        "Backend API for GTalk — Intelligent Audio and Text Conversion with AI. "
        "Supports audio transcription management, GeniVoice text-to-speech, "
        "user sessions, transcription history, and analytics dashboard."
    ),
    version="1.0.0",
)

# CORS — allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(auth.router, prefix="/api")
app.include_router(transcriptions.router, prefix="/api")
app.include_router(tts.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(views.router)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on application startup."""
    init_db()


@app.get("/")
def root():
    """Health check / root endpoint."""
    return {
        "app": "GTalk API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
