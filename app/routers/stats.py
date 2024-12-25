from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Player, Achieves, Plays, GameResult, Achievement  # Correct import
from app.dependencies import get_db

router = APIRouter()

@router.get("/GetPlayerStats/{username}")
async def get_player_stats(username: str, db: Session = Depends(get_db)):
    # Validate player existence
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Retrieve achievements
    achievements = (
        db.query(
            Achievement.name,
            Achievement.description
        )
        .join(Achieves, Achieves.achieve_id == Achievement.achieve_id)
        .filter(Achieves.username == username)
        .all()
    )

    # Calculate number of wins and losses
    stats = (
        db.query(
            func.count(Plays.win_or_lose).label("count"),
            Plays.win_or_lose
        )
        .filter(Plays.username == username)
        .group_by(Plays.win_or_lose)
        .all()
    )

    win_count = sum(count for count, result in stats if result == GameResult.WIN)
    lose_count = sum(count for count, result in stats if result == GameResult.LOSE)

    return {
        "username": username,
        "achievements": [{"name": name, "description": description} for name, description in achievements],
        "stats": {
            "wins": win_count,
            "losses": lose_count
        }
    }
