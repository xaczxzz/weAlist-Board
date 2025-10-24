"""
인증 및 JWT 검증 모듈

Member 서비스와 동일한 SECRET_KEY를 공유하여 JWT 토큰 검증
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import settings
from app.logging_config import get_logger
from uuid import UUID

logger = get_logger(__name__)

# HTTP Bearer 토큰 스키마
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    JWT 토큰에서 user_id를 추출

    Member 서비스에서 발급한 JWT 토큰을 검증하고 user_id를 반환합니다.

    Args:
        credentials: HTTP Authorization Bearer 토큰

    Returns:
        UUID: 사용자 ID

    Raises:
        HTTPException: 토큰이 유효하지 않을 경우 401 에러
    """
    token = credentials.credentials

    try:
        # JWT 디코딩 (Member 서비스와 같은 SECRET_KEY 사용)
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # user_id 추출 (JWT의 "sub" 클레임)
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"JWT validated successfully for user_id: {user_id}")
        return UUID(user_id)

    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UUID]:
    """
    선택적 인증 - 토큰이 있으면 user_id 반환, 없으면 None

    공개 API에서 사용 (인증된 사용자는 추가 정보 제공 가능)

    Args:
        credentials: HTTP Authorization Bearer 토큰 (선택)

    Returns:
        Optional[UUID]: 사용자 ID 또는 None
    """
    if credentials is None:
        return None

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        return UUID(user_id) if user_id else None
    except JWTError:
        return None
