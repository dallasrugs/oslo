from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers.routes import router
from internal import status
from internal.logger import logger
from fastapi.responses import JSONResponse


origins = [
    "*"]



supabase_listener_task = None  # Global task reference (optional, for shutdown)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Oslo v0.1")
    status.startup()
    yield
    logger.info("Shutting down Oslo...")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range"]
)

@app.middleware("http")
async def log_request_body(request: Request, call_next):
    try:
        body = await request.body()
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type or "text" in content_type:
            print(f"Request body: {body.decode('utf-8')}")
        else:
            print(f"Request body skipped (content-type: {content_type})")
    except Exception as e:
        print(f"Error reading body: {e}")
    
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the exception here if needed
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."}
    )

# call routers here
app.include_router(router, prefix="/api/v1", tags=["GSBAN Console API"])
