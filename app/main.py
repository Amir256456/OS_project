from fastapi import FastAPI
from app.routers import players, icons, achievements, games
from app.models import Base
from app.database import SessionLocal, engine  
from app.routers import icons

# Initialize FastAPI app
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(players.router, prefix="/players", tags=["Players"])
app.include_router(icons.router, prefix="/icons", tags=["Icons"])
app.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])
app.include_router(games.router, prefix="/games", tags=["Games"])

@app.get("/")
async def check():
    return "Add /docs to URL to open the Swagger"
