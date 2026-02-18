from abc import ABC, abstractmethod
from note.domain.model import Note


class INoteRepository(ABC):
    @abstractmethod
    async def get_notes(
        self, user_id: str, page: int, items_per_page: int
    ) -> tuple[int, list[Note]]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, user_id: str, id: str) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def save(self, user_id: str, note: Note) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user_id: str, note: Note) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: str, id: str) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def delete_tags(self, user_id: str, id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_notes_by_tag_name(
        self, user_id: str, tag_name: str, page: int, items_per_page: int
    ) -> tuple[int, list[Note]]:
        raise NotImplementedError
