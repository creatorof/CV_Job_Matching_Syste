from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import job 
from app.api.routes import auth 
from app.api.routes import cv 
from app.api.routes import recommendation
from app.core.config import settings
from app.database.db import create_tables

create_tables()

app = FastAPI(
    title="CV-Job Matching System API",
    description="Intelligent CV parsing and job recommendation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix=settings.API_PREFIX, tags=["auth"])
app.include_router(cv.router, prefix=settings.API_PREFIX, tags=["cvs"])
app.include_router(job.router, prefix=settings.API_PREFIX, tags=["jobs"])
app.include_router(recommendation.router, prefix=settings.API_PREFIX, tags=["recommendations"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)