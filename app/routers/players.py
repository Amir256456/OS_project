from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.schemas.player import PlayerBase, Login, PlayerOut
from app.models import Player
from app.dependencies import get_db
from app.utils import hash_password, verify_password

router = APIRouter()

@router.post('/RegisterPlayer', status_code=status.HTTP_201_CREATED)
async def register_player(player: PlayerBase, db: Session = Depends(get_db)):
    # Check if the username already exists
    existing_player = db.query(Player).filter(Player.username == player.username).first()
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists. Please choose a different username."
        )
    
    # Hash the password before storing it
    hashed_password = hash_password(player.password)
    player.password = hashed_password

    new_player = Player(**player.dict())
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player

@router.post('/LoginPlayer', status_code=status.HTTP_200_OK, response_model=PlayerOut)
async def login(player: Login, db: Session = Depends(get_db)):  # Use the Login schema here
    # Find player by username
    db_player = db.query(Player).filter(Player.username == player.username).first()
    if not db_player:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify password
    if not verify_password(player.password, db_player.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Return player details without password
    return db_player  # This will be converted to PlayerOut automatically because of the response_model

@router.get('/GetPlayer', response_model=PlayerOut)
async def get_player(username: str, db: Session = Depends(get_db)):
    # Find player by username
    db_player = db.query(Player).filter(Player.username == username).first()
    if not db_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    # Return player details without password
    return db_player  # This will be converted to PlayerOut automatically because of the response_model
