from ulid import ULID
from datetime import datetime
from fastapi import HTTPException
from dependency_injector.wiring import inject

from user.domain.user import User, Profile
from user.domain.repository.user_repo import IUserRepository
from utils.crypto import Crpyto


class UserService:
    @inject
    def __init__(self, user_repo: IUserRepository):
        self.user_repo: IUserRepository = user_repo
        self.ulid = ULID()
        self.crypto = Crpyto()

    async def create_user(self, name: str, email: str, password: str):
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
            created_at=now,
            updated_at=now,
        )
        await self.user_repo.save(user)
        return user
