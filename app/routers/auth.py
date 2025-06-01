import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from jose import jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import User
from app.utils.response import api_response

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_URL = "https://kapi.kakao.com/v2/user/me"

FRONTEND_REDIRECT_URI = os.getenv("FRONTEND_REDIRECT_URI")

router = APIRouter()


@router.get("/auth/kakao/login")
async def login_kakao():
    kakao_auth_redirect_url = (
        f"{KAKAO_AUTH_URL}?response_type=code&client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
    )
    return RedirectResponse(kakao_auth_redirect_url)


@router.get("/auth/kakao/callback")
async def kakao_callback(code: str, db: Session = Depends(get_db)):
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        token_res = await client.post(KAKAO_TOKEN_URL, data=data)
        token_json = token_res.json()
        access_token = token_json.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail=token_json)

        headers = {"Authorization": f"Bearer {access_token}"}
        user_res = await client.get(KAKAO_USER_URL, headers=headers)
        user_json = user_res.json()
        kakao_id = user_json.get("id")
        nickname = (
                user_json.get("properties", {}).get("nickname")
                or user_json.get("kakao_account", {}).get("profile", {}).get("nickname")
        )
        if not kakao_id:
            raise HTTPException(status_code=400, detail="카카오 사용자 정보를 가져올 수 없습니다.")

        user = db.query(User).filter(User.kakao_id == str(kakao_id)).first()
        if not user:
            user = User(
                kakao_id=str(kakao_id),
                nickname=nickname
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        token = jwt.encode({"sub": str(user.id)}, JWT_SECRET_KEY)

        return RedirectResponse(url=f"{FRONTEND_REDIRECT_URI}/auth/callback?token={token}")


@router.get('/auth/me')
async def get_current_user_info(user=Depends(get_current_user)):
    return api_response({
        "id": user.id,
        "kakao_id": user.kakao_id,
        "nickname": user.nickname,
        "created_at": user.created_at.isoformat()
    })
