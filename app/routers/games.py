from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Game, Player, Plays, Role, Team, GameResult
from app.dependencies import get_db

router = APIRouter()

@router.post("/AddPlayerToMatch")
async def add_player_to_match(
    username: str, 
    game_id: int, 
    team: Team, 
    game_pass: str | None = None, 
    db: Session = Depends(get_db)
):
    # Validate game existence
    game = db.query(Game).filter(Game.game_id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if the game is private and validate the game_pass
    if game.game_type == "PRIVATE":
        if not game_pass:
            raise HTTPException(status_code=400, detail="Game pass is required for a private game.")
        if game.game_pass != game_pass:
            raise HTTPException(status_code=403, detail="Invalid game pass.")

    # Validate player existence
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Check if the player is already in the match
    existing_record = db.query(Plays).filter(
        Plays.username == username,
        Plays.game_id == game_id
    ).first()
    if existing_record:
        raise HTTPException(status_code=400, detail="Player already added to this match")

    # Check total players in the game
    total_players = db.query(Plays).filter(Plays.game_id == game_id).count()
    if total_players >= 6:
        raise HTTPException(status_code=400, detail="A maximum of 6 players are allowed in one game.")

    # Add player to the match
    new_play = Plays(
        username=username,
        game_id=game_id,
        team=team,
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
async def change_player_role(username: str, game_id: int, round: int, role: Role, db: Session = Depends(get_db)):
    # Validate game existence
    game = db.query(Game).filter(Game.game_id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Validate player existence
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Validate player's participation in the match
    play_record = db.query(Plays).filter(
        Plays.username == username,
        Plays.game_id == game_id
    ).first()
    if not play_record:
        raise HTTPException(status_code=404, detail="Player not part of this match")

    # Validate roles in the same team for the current round
    team_roles = db.query(Plays).filter(
        Plays.game_id == game_id,
        Plays.team == play_record.team
    ).with_entities(
        Plays.role1 if round == 1 else Plays.role2 if round == 2 else Plays.role3
    ).all()
    
    if team_roles.count(role) >= 3:
        raise HTTPException(status_code=400, detail=f"Role {role} is already assigned to 3 players in the same team.")

    # Update the role based on the round
    if round == 1:
        play_record.role1 = role
    elif round == 2:
        play_record.role2 = role
    elif round == 3:
        play_record.role3 = role
    else:
        raise HTTPException(status_code=400, detail="Invalid round number. Must be 1, 2, or 3.")

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
async def end_game(game_id: int, team: Team, win_or_lose: GameResult, db: Session = Depends(get_db)):
    if win_or_lose not in ["WIN", "LOSE"]:
        raise HTTPException(status_code=400, detail="Invalid value for win_or_lose. Must be 'WIN' or 'LOSE'.")

    # Validate game existence
    game = db.query(Game).filter(Game.game_id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Update win_or_lose for all players in the game
    plays = db.query(Plays).filter(Plays.game_id == game_id).all()
    if not plays:
        raise HTTPException(status_code=404, detail="No players found for this game.")

    for play in plays:
        if play.team == team:
            play.win_or_lose = "WIN" if win_or_lose == "WIN" else "LOSE"
        else:
            play.win_or_lose = "LOSE" if win_or_lose == "WIN" else "WIN"

    db.commit()

    return {
        "message": f"Game {game_id} ended. Team {team} set to {win_or_lose}.",
    }
