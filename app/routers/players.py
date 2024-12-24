from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.schemas.player import PlayerBase, Login, PlayerOut
from app.models import Player, Icon
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
    
    # Check if the icon_id exists in the icons table
    icon_exists = db.query(Icon).filter(Icon.icon_id == player.icon_id).first()
    if not icon_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Icon not found."
        )
    
    # Calculate the correct age from b_date
    today = datetime.today()
    b_date = player.b_date
    calculated_age = today.year - b_date.year - ((today.month, today.day) < (b_date.month, b_date.day))

    # Compare the provided age with the calculated age
    if player.age != calculated_age:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided age does not match the birth date."
        )
    
    # Hash the password before storing it
    hashed_password = hash_password(player.password)

    # Create the new player record with the correct age
    new_player = Player(
        username=player.username,
        password=hashed_password,
        b_date=b_date,
        age=calculated_age,
        name=player.name,
        surname=player.surname,
        gender=player.gender,
        address=player.address,
        email=player.email,
        icon_id=player.icon_id
    )
    db.add(new_player)
    db.commit()
    db.refresh(new_player)

    return new_player

@router.post('/LoginPlayer', status_code=status.HTTP_200_OK, response_model=PlayerOut)
async def login(player: Login, db: Session = Depends(get_db)):
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
