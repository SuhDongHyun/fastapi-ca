from ulid import ULID
from datetime import datetime
from fastapi import HTTPException, status

from user.domain.user import User, Profile
from user.domain.repository.user_repo import IUserRepository
from utils.crypto import Crpyto
from utils.auth import create_access_token, Role


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo: IUserRepository = user_repo
        self.ulid = ULID()
        self.crypto = Crpyto()

    async def create_user(
        self, name: str, email: str, password: str, memo: str | None = None
    ):
        _user = None

        try:
            _user = await self.user_repo.find_by_email(email)
        except HTTPException as e:
            if e.status_code != 422:
                raise e

        if _user:
            raise HTTPException(status_code=422)

        now = datetime.now()
        profile = Profile(name=name, email=email)
        user: User = User(
            id=self.ulid.generate(),
            profile=profile,
            password=self.crypto.encrypt(password),
            memo=memo,
            created_at=now,
            updated_at=now,
        )
        await self.user_repo.save(user)
        return user

    async def update_user(
        self, user_id: str, name: str | None = None, password: str | None = None
    ):
        user = await self.user_repo.find_by_id(user_id)

        if name:
            user.profile.name = name
        if password:
            user.password = self.crypto.encrypt(password)
        user.updated_at = datetime.now()
        await self.user_repo.update(user)
        return user

    async def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        return await self.user_repo.get_users(page, items_per_page)

    async def delete_user(self, user_id: str):
        await self.user_repo.delete(user_id)

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repo.find_by_email(email)

        if not self.crypto.verify(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return create_access_token(payload={"user_id": user.id}, role=Role.USER)
