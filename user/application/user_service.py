from ulid import ULID
from datetime import datetime
from user.domain.user import User, Profile
from user.domain.repository.user_repo import IUserRepository
from user.infra.repository.user_repo import UserRepository
from fastapi import HTTPException
from utils.crypto import Crpyto


class UserService:
    def __init__(self):
        self.user_repo: IUserRepository = UserRepository()
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
