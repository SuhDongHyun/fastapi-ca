from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from dependency_injector.wiring import inject, Provide

from containers import Container
from user.application.user_service import UserService
from utils.auth import get_current_user, CurrentUser, get_admin_user

router = APIRouter(prefix="/users", tags=["users"])


class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)


class UpdateUserBody(BaseModel):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class GetUsersResponse(BaseModel):
    total_count: int
    page: int
    users: list[UserResponse]


@router.post("/login")
@inject
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    access_token = await user_service.login(
        email=form_data.username, password=form_data.password
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("", status_code=201, response_model=UserResponse)
@inject
async def create_user(
    user: CreateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    created_user = await user_service.create_user(
        name=user.name, email=user.email, password=user.password
    )

    return UserResponse(
        id=created_user.id,
        name=created_user.profile.name,
        email=created_user.profile.email,
        created_at=created_user.created_at,
        updated_at=created_user.updated_at,
    )


@router.put("", response_model=UserResponse)
@inject
async def update_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: UpdateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    updated_user = await user_service.update_user(
        user_id=current_user.user_id,
        name=body.name,
        password=body.password,
    )

    return UserResponse(
        id=updated_user.id,
        name=updated_user.profile.name,
        email=updated_user.profile.email,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )


@router.get("", response_model=GetUsersResponse)
@inject
async def get_users(
    page: int = 1,
    items_per_page: int = 10,
    current_user: CurrentUser = Depends(get_admin_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    total_count, users = await user_service.get_users(page, items_per_page)

    return {
        "total_count": total_count,
        "page": page,
        "users": [
            UserResponse(
                id=user.id,
                name=user.profile.name,
                email=user.profile.email,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in users
        ],
    }


@router.delete("/", status_code=204)
@inject
async def delete_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    await user_service.delete_user(user_id=current_user.user_id)
