from fastapi import Request, HTTPException, status
from typing import Dict, Optional
from app.bluegroups_auth import is_user_in_group


def get_current_user(request: Request) -> Dict:
    """
    Dependency to get current authenticated user from session
    """
    user = request.session.get('user')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user

from fastapi import Request, HTTPException, Depends

def get_current_active_user(request: Request):
    """
    Extracts the currently active user from session.
    This replaces old JWT token-based `get_current_active_user`.
    """
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user



def get_current_user_optional(request: Request) -> Optional[Dict]:
    """
    Dependency to get current user if authenticated, None otherwise
    """
    return request.session.get('user')


def require_groups(*allowed_groups):
    """
    Dependency factory to enforce BlueGroup-based access control.
    Usage: Depends(require_groups("Administrators", "Solution Architects"))
    """
    def dependency(current_user: dict = Depends(get_current_active_user)):
        email = current_user.get("email")

        # If no specific group is required (default catalog access)
        if not allowed_groups:
            return current_user

        # Check BlueGroups membership
        for group in allowed_groups:
            if is_user_in_group(email, group):
                return current_user

        # If user not in any of the required groups
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Must belong to one of: {', '.join(allowed_groups)}"
        )
    return dependency
