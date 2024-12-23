from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models import Achievement, Achieves, Player
from app.schemas.achievement import AchievementBase, AchievementOut
from app.dependencies import get_db

router = APIRouter()

# Add achievement to a player
@router.post('/AddPlayerAchievement', status_code=status.HTTP_201_CREATED)
async def add_player_achievement(achievement_id: int, username: str, db: Session = Depends(get_db)):
    # Check if the player exists
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Check if the achievement exists
    achievement = db.query(Achievement).filter(Achievement.achieve_id == achievement_id).first()
    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Achievement not found"
        )
    
    # Check if the player already has this achievement
    existing_record = db.query(Achieves).filter(
        Achieves.username == username,
        Achieves.achieve_id == achievement_id
    ).first()
    
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player already has this achievement"
        )
    
    # Add new achievement record to the Achieves table
    new_record = Achieves(username=username, achieve_id=achievement_id)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return {"message": "Achievement added to player successfully"}


# Get all achievements of a player
@router.get('/GetPlayerAchievements', response_model=list[AchievementOut])
async def get_player_achievements(username: str, db: Session = Depends(get_db)):
    # Query achievements of the player from the Achieves table
    player_achievements = db.query(Achievement).join(Achieves).filter(Achieves.username == username).all()

    if not player_achievements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No achievements found for this player"
        )
    
    return player_achievements


# Get achievements with optional ID (if ID provided, return that achievement, otherwise return all)
@router.get('/GetAllAchievements', response_model=list[AchievementOut])
async def get_all_achievements(id: int | None = None, db: Session = Depends(get_db)):
    if id:
        # If ID is provided, return the achievement with that ID
        achievement = db.query(Achievement).filter(Achievement.achieve_id == id).first()
        if not achievement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Achievement not found"
            )
        return [achievement]  # Return the single achievement in a list
    
    # If ID is not provided, return all achievements
    all_achievements = db.query(Achievement).all()
    
    if not all_achievements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No achievements found"
        )
    
    return all_achievements
