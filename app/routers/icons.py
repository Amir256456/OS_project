from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Icon
from app.dependencies import get_db

router = APIRouter()

@router.get("/GetIcon")
async def get_icons(id: Optional[int] = None, db: Session = Depends(get_db)):
    if id is not None:
        # Fetch the specific record by ID
        icon = db.query(Icon).filter(Icon.icon_id == id).first()
        if icon is None:
            raise HTTPException(status_code=404, detail="Icon not found")
        return {"icon": icon}  # Return the icon object directly
    
    # Fetch all records if no ID is provided
    icons = db.query(Icon).all()
    return {"icons": icons}  # Return all icons
