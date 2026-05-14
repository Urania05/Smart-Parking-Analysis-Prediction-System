from fastapi import HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
import database
import models

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def get_current_user(
    api_key: str = Security(api_key_header), 
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.api_key == api_key).first()
    
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key!")
    
    return user

def require_role(required_role: models.Role):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=401, 
                detail=f"Permission Denied: This action requires the {required_role.value} role ."
            )
        return current_user
    return role_checker