from fastapi import FastAPI

from backend.app.auth.router import router as auth_router
from backend.app.enrollment.router import router as enrollment_router
from backend.app.finance.router import router as finance_router
from backend.app.verification.router import router as verification_router


app = FastAPI(
    title="AI-Powered Adaptive University Learning Platform",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(enrollment_router)
app.include_router(finance_router)
app.include_router(verification_router)


@app.get("/")
def root():
    return {
        "message": "AI University Platform API is running"
    }