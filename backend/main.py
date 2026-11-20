from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.request import router as request_router
from app.api.v1.progress import router as progress_router
from app.api.v1.analytics import router as analytics_router

app = FastAPI()




app.include_router(progress_router,prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(request_router,prefix="/api/v1")
app.include_router(analytics_router,prefix="/api/v1")

@app.get("/")
def home():
    return {
        "message":"Server is Healthy!"
    }
