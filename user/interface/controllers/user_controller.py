from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from dependency_injector.wiring import inject, Provide
from containers import Container

from user.application.user_service import UserService

router = APIRouter(prefix="/users")


class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)


class UpdateUser(BaseModel):
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


@router.post("", status_code=201, response_model=UserResponse)
@inject
async def create_user(
    user: CreateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    created_user = await user_service.create_user(
        name=user.name, email=user.email, password=user.password
    )

    return created_user


@router.post("/{user_id}")
@inject
async def update_user(
    user_id: str,
    user: UpdateUser,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    updated_user = await user_service.update_user(
        user_id=user_id,
        name=user.name,
        password=user.password,
    )

    return updated_user


@router.get("", response_model=GetUsersResponse)
@inject
async def get_users(
    page: int = 1,
    items_per_page: int = 10,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    total_count, users = await user_service.get_users(page, items_per_page)

    return {
        "total_count": total_count,
        "page": page,
        "users": users,
    }


@router.delete("/", status_code=204)
@inject
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    await user_service.delete_user(user_id)
