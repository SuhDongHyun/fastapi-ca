from sqlalchemy import select, func
from fastapi import HTTPException

from database import session_scope
from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User as UserVO, Profile
from user.infra.model.user import User


class UserRepository(IUserRepository):
    async def save(self, user: UserVO):
        async with session_scope() as session:
            new_user = User(
                id=user.id,
                name=user.profile.name,
                email=user.profile.email,
                password=user.password,
                memo=user.memo,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

            session.add(new_user)

    async def find_by_email(self, email: str) -> UserVO:
        async with session_scope() as session:
            stmt = select(User).where(User.email == email).limit(1)
            res = await session.execute(stmt)
            user = res.scalars().first()
            if not user:
                raise HTTPException(status_code=422)

            return UserVO(
                id=user.id,
                profile=Profile(name=user.name, email=user.email),
                password=user.password,
                memo=user.memo,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

    async def find_by_id(self, id: str) -> UserVO:
        async with session_scope() as session:
            stmt = select(User).where(User.id == id).limit(1)
            res = await session.execute(stmt)
            user = res.scalars().first()

            if not user:
                raise HTTPException(status_code=422)

            return UserVO(
                id=user.id,
                profile=Profile(name=user.name, email=user.email),
                password=user.password,
                memo=user.memo,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

    async def update(self, user_vo: UserVO):
        async with session_scope() as session:
            stmt = select(User).where(User.id == user_vo.id).limit(1)
            res = await session.execute(stmt)
            user = res.scalars().first()

            if user is None:
                raise HTTPException(status_code=422)

            user.name = user_vo.profile.name
            user.password = user_vo.password

            session.add(user)

    async def get_users(
        self, page: int = 1, items_per_page: int = 10
    ) -> tuple[int, list[UserVO]]:
        async with session_scope() as session:
            stmt = select(func.count()).select_from(User)
            res = await session.execute(stmt)
            total_count = res.scalar_one()

            offset = (page - 1) * items_per_page
            stmt = select(User).offset(offset).limit(items_per_page)
            res = await session.execute(stmt)
            users = res.scalars().all()

            return total_count, [
                UserVO(
                    id=user.id,
                    profile=Profile(name=user.name, email=user.email),
                    password=user.password,
                    memo=user.memo,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )
                for user in users
            ]

    async def delete(self, id: str):
        async with session_scope() as session:
            stmt = select(User).where(User.id == id).limit(1)
            res = await session.execute(stmt)
            user = res.scalars().first()

            if user is None:
                raise HTTPException(status_code=422)

            await session.delete(user)
