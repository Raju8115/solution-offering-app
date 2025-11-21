from fastapi import Depends, HTTPException, status
from app.auth.dependencies import get_current_active_user
from app.bluegroups_auth import is_user_in_group
import logging
from app.config import settings

# ADMIN_GROUP = "Admiin"
# SOLUTION_ARCHITECT_GROUP = "Solution"
ADMIN_GROUP = settings.ADMIN_BLUEGROUP
SOLUTION_ARCHITECT_GROUP = settings.SOLUTION_ARCHITECT_BLUEGROUP

logger = logging.getLogger(__name__)

# BlueGroup names - Update these with your actual BlueGroup names

async def require_admin(current_user: dict = Depends(get_current_active_user)):
    """
    Require user to be in Administrators BlueGroup.
    Grants full access to modify offerings, activities, pricing, etc.
    """
    email = current_user.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not found in user profile"
        )
    
    if not is_user_in_group(email, ADMIN_GROUP):
        logger.warning(f"User {email} attempted admin action without permission")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required. Contact your administrator to request access."
        )
    
    logger.info(f"Admin access granted to {email}")
    return current_user

async def require_solution_architect(current_user: dict = Depends(get_current_active_user)):
    """
    Require user to be in Solution Architects BlueGroup or Administrators.
    Grants access to solution builder (link/unlink activities, update sequences).
    Admins automatically have Solution Architect permissions.
    """
    email = current_user.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not found in user profile"
        )
    
    # Admins have all permissions including solution architect
    if is_user_in_group(email, ADMIN_GROUP):
        logger.info(f"Solution Architect access granted to {email} (via Admin role)")
        return current_user
    
    if not is_user_in_group(email, SOLUTION_ARCHITECT_GROUP):
        logger.warning(f"User {email} attempted solution architect action without permission")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solution Architect access required. Contact your administrator to request access."
        )
    
    logger.info(f"Solution Architect access granted to {email}")
    return current_user

async def get_user_roles(current_user: dict = Depends(get_current_active_user)):
    """
    Get user roles for UI display.
    Returns a dict with role flags.
    """
    
    email = current_user.get("email")
    if not email:
        return {
            "is_admin": False,
            "is_solution_architect": False,
            "has_catalog_access": True
        }
    
    is_admin = is_user_in_group(email, ADMIN_GROUP)
    # is_admin = False
    is_solution_architect = is_admin or is_user_in_group(email, SOLUTION_ARCHITECT_GROUP)
    
    

    return {
        "is_admin": is_admin,
        "is_solution_architect": is_solution_architect,
        "has_catalog_access": True,
        "email": email
    }