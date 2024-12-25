from pydantic import BaseModel
from app.models import Role, Team, GameResult

# Request schemas
class AddPlayerToMatchRequest(BaseModel):
    username: str
    match_id: str
    team: Team
    game_pass: str | None = None


class ChangePlayerRoleRequest(BaseModel):
    username: str
    match_id: str
    round: int
    role: Role

class EndGameRequest(BaseModel):
    match_id: str
    team: Team
    win_or_lose: GameResult