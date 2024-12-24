from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Game, Player, Plays, Role, Team, GameResult
from app.dependencies import get_db
from app.schemas.game import AddPlayerToMatchRequest, ChangePlayerRoleRequest, EndGameRequest

router = APIRouter()

# CreateMatch endpoint
@router.post("/CreateMatch")
async def create_match(
    game_pass: str | None = None, 
    db: Session = Depends(get_db)
):

    # Create the game instance
    new_game = Game(
        game_type="PRIVATE" if game_pass else "PUBLIC",
        game_pass=game_pass if game_pass else None,
        status="STARTED",
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    return {
        "game_id": new_game.game_id,
        "game_type": new_game.game_type,
        "game_pass": new_game.game_pass,
        "status": new_game.status,
    }

@router.post("/AddPlayerToMatch")
async def add_player_to_match(request: AddPlayerToMatchRequest, db: Session = Depends(get_db)):
    # Validate game existence
    game = db.query(Game).filter(Game.game_id == request.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if the game is private and validate the game_pass
    if game.game_type == "PRIVATE":
        if not request.game_pass:
            raise HTTPException(status_code=400, detail="Game pass is required for a private game.")
        if game.game_pass != request.game_pass:
            raise HTTPException(status_code=403, detail="Invalid game pass.")

    # Validate player existence
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Check if the player is already in the match
    existing_record = db.query(Plays).filter(
        Plays.username == request.username,
        Plays.game_id == request.game_id
    ).first()
    if existing_record:
        raise HTTPException(status_code=400, detail="Player already added to this match")

    # Check total players in the game
    total_players = db.query(Plays).filter(Plays.game_id == request.game_id).count()
    if total_players >= 6:
        raise HTTPException(status_code=400, detail="A maximum of 6 players are allowed in one game.")

    # Add player to the match
    new_play = Plays(
        username=request.username,
        game_id=request.game_id,
        team=request.team,
        role1=None,
        role2=None,
        role3=None,
        win_or_lose=None
    )
    db.add(new_play)
    db.commit()
    db.refresh(new_play)

    return {
        "message": "Player added to match successfully",
        "username": new_play.username,
        "game_id": new_play.game_id,
        "team": new_play.team,
        "roles": {
            "role1": new_play.role1,
            "role2": new_play.role2,
            "role3": new_play.role3
        },
        "win_or_lose": new_play.win_or_lose
    }

@router.put("/ChangePlayerRole")
async def change_player_role(request: ChangePlayerRoleRequest, db: Session = Depends(get_db)):
    # Validate game existence
    game = db.query(Game).filter(Game.game_id == request.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Validate player existence
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Validate player's participation in the match
    play_record = db.query(Plays).filter(
        Plays.username == request.username,
        Plays.game_id == request.game_id
    ).first()
    if not play_record:
        raise HTTPException(status_code=404, detail="Player not part of this match")

    # Validate roles in the same team for the current round
    # Checking whether the requested role is already assigned to another player in the same team
    if request.round == 1:
        existing_role = db.query(Plays).filter(
            Plays.game_id == request.game_id,
            Plays.team == play_record.team,
            Plays.role1 == request.role
        ).first()
    elif request.round == 2:
        existing_role = db.query(Plays).filter(
            Plays.game_id == request.game_id,
            Plays.team == play_record.team,
            Plays.role2 == request.role
        ).first()
    elif request.round == 3:
        existing_role = db.query(Plays).filter(
            Plays.game_id == request.game_id,
            Plays.team == play_record.team,
            Plays.role3 == request.role
        ).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid round number. Must be 1, 2, or 3.")

    # If the role is already assigned to another player, raise an error
    if existing_role:
        raise HTTPException(status_code=400, detail=f"Role '{request.role}' is already assigned to another player in team {play_record.team} for round {request.round}.")

    # Update the role based on the round
    if request.round == 1:
        play_record.role1 = request.role
    elif request.round == 2:
        play_record.role2 = request.role
    elif request.round == 3:
        play_record.role3 = request.role

    db.commit()
    db.refresh(play_record)

    return {
        "message": "Player role updated successfully",
        "username": play_record.username,
        "game_id": play_record.game_id,
        "roles": {
            "role1": play_record.role1,
            "role2": play_record.role2,
            "role3": play_record.role3
        }
    }

@router.put("/EndGame")
async def end_game(request: EndGameRequest, db: Session = Depends(get_db)):
    if request.win_or_lose not in ["WIN", "LOSE"]:
        raise HTTPException(status_code=400, detail="Invalid value for win_or_lose. Must be 'WIN' or 'LOSE'.")

    # Validate game existence
    game = db.query(Game).filter(Game.game_id == request.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Update win_or_lose for all players in the game
    plays = db.query(Plays).filter(Plays.game_id == request.game_id).all()
    if not plays:
        raise HTTPException(status_code=404, detail="No players found for this game.")

    for play in plays:
        if play.team == request.team:
            play.win_or_lose = "WIN" if request.win_or_lose == "WIN" else "LOSE"
        else:
            play.win_or_lose = "LOSE" if request.win_or_lose == "WIN" else "WIN"

    db.commit()

    return {
        "message": f"Game {request.game_id} ended. Team {request.team} set to {request.win_or_lose}.",
    }
