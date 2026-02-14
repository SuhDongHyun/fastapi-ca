from abc import ABCMeta, abstractmethod
from user.domain.user import User


class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, user: User):
        raise NotImplementedError

    @abstractmethod
    async def find_by_email(self, email: str) -> User:
        """
        이메일로 유저를 검색한다.
        검색한 유저가 없을 경우 422 에러를 발생시킨다.
        """
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User):
        raise NotImplementedError

    @abstractmethod
    async def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: str):
        raise NotImplementedError
