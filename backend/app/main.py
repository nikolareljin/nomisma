from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .routes import coins, microscope, ai, ebay, auth

app = FastAPI(
    title="Nomisma API",
    description="Coin analysis and cataloging system with AI-powered valuation",
    version="1.0.0"
)

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for images
images_path = os.getenv("IMAGES_PATH", "/app/images")
os.makedirs(images_path, exist_ok=True)
app.mount("/images", StaticFiles(directory=images_path), name="images")

# Include routers
app.include_router(auth.router)  # Auth routes (no prefix, already has /api/auth)
app.include_router(coins.router, prefix="/api/coins", tags=["Coins"])
app.include_router(microscope.router, prefix="/api/microscope", tags=["Microscope"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Analysis"])
app.include_router(ebay.router, prefix="/api/ebay", tags=["eBay"])

@app.get("/")
async def root():
    return {
        "name": "Nomisma API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
