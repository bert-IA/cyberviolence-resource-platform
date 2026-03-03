"""
Module d'authentification centralisé.

Toutes les fonctions d'auth sont ici pour éviter les imports circulaires
qui existaient quand verify_admin_token était dans admin_api.py.

Usage dans un router :
    from routers.auth import verify_admin_token
    from fastapi import Depends

    @router.post("/my-endpoint")
    async def my_endpoint(request: Request, admin_id: str = Depends(verify_admin_token)):
        ...
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from constants import ADMIN_TOKEN_DEV

security = HTTPBearer()


def verify_admin_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Vérifie le token Bearer et retourne l'admin_id.

    Injecter via Depends() dans chaque endpoint protégé.
    Retourne "admin_user" si le token est valide.
    Lève HTTPException 401 sinon.

    Note production : remplacer ADMIN_TOKEN_DEV par une vérification
    JWT ou base de données, et passer admin_id dynamiquement
    (pas hardcodé) pour la traçabilité des actions.
    """
    if credentials.credentials != ADMIN_TOKEN_DEV:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'accès invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return "admin_user"
