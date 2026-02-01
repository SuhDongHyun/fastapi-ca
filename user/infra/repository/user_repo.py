from sqlalchemy import select
from fastapi import HTTPException

from database import get_session
from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User as UserVO, Profile
from user.infra.model.user import User


class UserRepository(IUserRepository):
    async def save(self, user: UserVO):
        new_user = User(
            id=user.id,
            name=user.profile.name,
            email=user.profile.email,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        agen = get_session()
        session = await agen.__anext__()

        try:
            session.add(new_user)
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await agen.aclose()

    async def find_by_email(self, email: str) -> UserVO:
        agen = get_session()
        session = await agen.__anext__()

        try:
            stmt = select(User).where(User.email == email).limit(1)
            res = await session.execute(stmt)
            user = res.scalars().first()
        finally:
            await agen.aclose()

        if not user:
            raise HTTPException(status_code=422)

        return UserVO(
            id=user.id,
            profile=Profile(name=user.name, email=user.email),
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
