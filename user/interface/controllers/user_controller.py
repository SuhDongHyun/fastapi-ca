from fastapi import APIRouter, Depends
from pydantic import BaseModel
from dependency_injector.wiring import inject, Provide
from containers import Container

from user.application.user_service import UserService

router = APIRouter(prefix="/users")


class CreateUserBody(BaseModel):
    name: str
    email: str
    password: str


class UpdateUser(BaseModel):
    name: str | None = None
    password: str | None = None


@router.post("", status_code=201)
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
