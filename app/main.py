from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager
from routers.routes import router
from internal import status
from internal.logger import logger
from fastapi.responses import JSONResponse


origins = [
    "http://localhost:3000"]




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Call DB check via status (and in future: other services too)
    logger.info("Starting up GSBAN Console API v0.1")
    status.startup()
    yield
    logger.info("Shutting down API...")



app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the exception here if needed
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."}
    )

# call routers here
app.include_router(router, prefix="/api/v1", tags=["GSBAN Console API"])
