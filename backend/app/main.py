from fastapi import FastAPI

from backend.app.auth.router import router as auth_router
from backend.app.enrollment.router import router as enrollment_router


app = FastAPI(
    title="AI-Powered Adaptive University Learning Platform",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(enrollment_router)


@app.get("/")
def root():
    return {
        "message": "AI University Platform API is running"
    }