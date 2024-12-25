from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Game, Player, Plays, Role, Team, GameResult, GameStatus
from app.dependencies import get_db
from app.schemas.game import AddPlayerToMatchRequest, ChangePlayerRoleRequest, EndGameRequest

router = APIRouter()

# CreateMatch endpoint
@router.post("/CreateMatch")
async def create_match(
    match_id: str,
    game_pass: str | None = None, 
    db: Session = Depends(get_db)
):
    # Check if a game with the given match_id already exists
    existing_game = db.query(Game).filter(Game.match_id == match_id).first()
    if existing_game:
        raise HTTPException(status_code=400, detail="A game with this match_id already exists.")
    
    # Create the game instance
    new_game = Game(
        match_id=match_id,
        game_type="PRIVATE" if game_pass else "PUBLIC",
        game_pass=game_pass if game_pass else None,
        status="STARTED",
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    return {
        "game_id": new_game.match_id,
        "game_type": new_game.game_type,
        "game_pass": new_game.game_pass,
        "status": new_game.status,
    }


# AddPlayerToMatch endpoint
@router.post("/AddPlayerToMatch")
async def add_player_to_match(request: AddPlayerToMatchRequest, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.match_id == request.match_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.game_type == "PRIVATE":
        if not request.game_pass or game.match_pass != request.game_pass:
            raise HTTPException(status_code=403, detail="Invalid or missing game pass.")

    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    existing_record = db.query(Plays).filter(
        Plays.username == request.username,
        Plays.match_id == request.match_id
    ).first()
    if existing_record:
        raise HTTPException(status_code=400, detail="Player already added to this match")

    if db.query(Plays).filter(Plays.match_id == request.match_id).count() >= 6:
        raise HTTPException(status_code=400, detail="A maximum of 6 players are allowed in one game.")

    new_play = Plays(
        username=request.username,
        match_id=request.match_id,
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
        "match_id": new_play.match_id,
        "team": new_play.team,
        "roles": {
            "role1": new_play.role1,
            "role2": new_play.role2,
            "role3": new_play.role3
        },
        "win_or_lose": new_play.win_or_lose
    }

# ChangePlayerRole endpoint
@router.put("/ChangePlayerRole")
async def change_player_role(request: ChangePlayerRoleRequest, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.match_id == request.match_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    play_record = db.query(Plays).filter(
        Plays.username == request.username,
        Plays.match_id == request.match_id
    ).first()
    if not play_record:
        raise HTTPException(status_code=404, detail="Player not part of this match")

    existing_role = None
    if request.round == 1:
        existing_role = db.query(Plays).filter(
            Plays.match_id == request.match_id,
            Plays.team == play_record.team,
            Plays.role1 == request.role
        ).first()
    elif request.round == 2:
        existing_role = db.query(Plays).filter(
            Plays.match_id == request.match_id,
            Plays.team == play_record.team,
            Plays.role2 == request.role
        ).first()
    elif request.round == 3:
        existing_role = db.query(Plays).filter(
            Plays.match_id == request.match_id,
            Plays.team == play_record.team,
            Plays.role3 == request.role
        ).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid round number. Must be 1, 2, or 3.")

    if existing_role:
        raise HTTPException(status_code=400, detail=f"Role '{request.role}' is already assigned in team {play_record.team}.")

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
        "match_id": play_record.match_id,
        "roles": {
            "role1": play_record.role1,
            "role2": play_record.role2,
            "role3": play_record.role3
        }
    }

# EndGame endpoint
@router.put("/EndGame")
async def end_game(request: EndGameRequest, db: Session = Depends(get_db)):
    try:
        # Convert the input string to the GameResult enum
        result = GameResult(request.win_or_lose.value.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid value for win_or_lose. Must be 'WIN' or 'LOSE'.")

    # Validate game existence
    game = db.query(Game).filter(Game.match_id == request.match_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Validate players in the game
    plays = db.query(Plays).filter(Plays.match_id == request.match_id).all()
    if not plays:
        raise HTTPException(status_code=404, detail="No players found for this game.")

    # Update win_or_lose for all players in the game
    for play in plays:
        if play.team == request.team:
            play.win_or_lose = GameResult.WIN if result == GameResult.WIN else GameResult.LOSE
        else:
            play.win_or_lose = GameResult.LOSE if result == GameResult.WIN else GameResult.WIN

    # Mark game as finished
    game.status = GameStatus.FINISHED
    db.commit()

    return {
        "message": f"Game {request.match_id} ended. Team {request.team} set to {request.win_or_lose}.",
    }

