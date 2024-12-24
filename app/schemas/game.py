from pydantic import BaseModel
from app.models import Role, Team, GameResult

# Request schemas
class AddPlayerToMatchRequest(BaseModel):
    username: str
    game_id: int
    team: Team
    game_pass: str | None = None


class ChangePlayerRoleRequest(BaseModel):
    username: str
    game_id: int
    round: int
    role: Role

class EndGameRequest(BaseModel):
    game_id: int
    team: Team
    win_or_lose: GameResult