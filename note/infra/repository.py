from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from database import session_scope
from note.domain.model import Note as NoteVO
from note.domain.repository import INoteRepository
from note.infra.model import Note, Tag
from utils.db_utils import row_to_dict


class NoteRepository(INoteRepository):
    async def get_notes(
        self,
        user_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[NoteVO]]:
        async with session_scope() as session:
            stmt = (
                select(Note)
                .options(joinedload(Note.tags))
                .where(Note.user_id == user_id)
                .offset((page - 1) * items_per_page)
                .limit(items_per_page)
            )

            res = await session.execute(stmt)
            notes = res.unique().scalars().all()

            count_stmt = select(func.count(Note.id)).where(Note.user_id == user_id)
            total_count = await session.execute(count_stmt)

            note_vos = [NoteVO(**row_to_dict(note)) for note in notes]

            return total_count.scalar_one(), note_vos

    async def find_by_id(self, user_id: str, id: str) -> NoteVO:
        async with session_scope() as session:
            stmt = (
                select(Note)
                .options(joinedload(Note.tags))
                .where(Note.user_id == user_id, Note.id == id)
            )
            res = await session.execute(stmt)
            note = res.scalars().first()

            if not note:
                raise HTTPException(status_code=422)

            return NoteVO(**row_to_dict(note))

    async def save(self, user_id: str, note_vo: NoteVO):
        async with session_scope() as session:
            tags: list[Tag] = []
            for tag in note_vo.tags:
                stmt = select(Tag).filter(Tag.name == tag.name)
                res = await session.execute(stmt)
                existing_tag = res.scalars().first()
                if existing_tag:
                    tags.append(existing_tag)
                else:
                    tags.append(
                        Tag(
                            id=tag.id,
                            name=tag.name,
                            created_at=tag.created_at,
                            updated_at=tag.updated_at,
                        )
                    )

            new_note = Note(
                id=note_vo.id,
                user_id=user_id,
                title=note_vo.title,
                content=note_vo.content,
                memo_date=note_vo.memo_date,
                tags=tags,
                created_at=note_vo.created_at,
                updated_at=note_vo.updated_at,
            )
            session.add(new_note)

    async def update(self, user_id: str, note_vo: NoteVO) -> NoteVO:
        async with session_scope() as session:
            await self.delete_tags(user_id, note_vo.id)
            stmt = (
                select(Note)
                .options(joinedload(Note.tags))
                .where(Note.user_id == user_id, Note.id == note_vo.id)
            )
            res = await session.execute(stmt)
            note = res.unique().scalars().first()
            if not note:
                raise HTTPException(status_code=422)
            note.title = note_vo.title
            note.content = note_vo.content
            note.memo_date = note_vo.memo_date

            tags: list[Tag] = []
            for tag in note_vo.tags:
                stmt = select(Tag).filter(Tag.name == tag.name)
                res = await session.execute(stmt)
                existing_tag = res.scalars().first()
                if existing_tag:
                    tags.append(existing_tag)
                else:
                    tags.append(
                        Tag(
                            id=tag.id,
                            name=tag.name,
                            created_at=tag.created_at,
                            updated_at=tag.updated_at,
                        )
                    )

            note.tags = tags
            session.add(note)
            return NoteVO(**row_to_dict(note))

    async def delete_tags(self, user_id: str, id: str):
        async with session_scope() as session:
            stmt = (
                select(Note)
                .options(joinedload(Note.tags))
                .where(Note.user_id == user_id, Note.id == id)
            )
            res = await session.execute(stmt)
            note = res.unique().scalars().first()
            if not note:
                raise HTTPException(status_code=422)

            note.tags = []
            session.add(note)

            unused_tags_stmt = select(Tag).where(~Tag.notes.any())
            res = await session.execute(unused_tags_stmt)
            unused_tags = res.scalars().all()
            for tag in unused_tags:
                await session.delete(tag)

    async def delete(self, user_id: str, id: str):
        async with session_scope() as session:
            await self.delete_tags(user_id, id)

            stmt = select(Note).where(Note.user_id == user_id, Note.id == id)
            res = await session.execute(stmt)
            note = res.scalars().first()
            if not note:
                raise HTTPException(status_code=422)

            await session.delete(note)

    async def get_notes_by_tag_name(
        self,
        user_id: str,
        tag_name: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[NoteVO]]:
        async with session_scope() as session:
            tag_stmt = select(Tag).where(Tag.name == tag_name)
            res = await session.execute(tag_stmt)
            tag = res.scalars().first()

            if not tag:
                return 0, []

            stmt = (
                select(Note)
                .options(joinedload(Note.tags))
                .where(
                    Note.user_id == user_id,
                    Note.tags.any(id=tag.id),
                )
                .offset((page - 1) * items_per_page)
                .limit(items_per_page)
            )

            res = await session.execute(stmt)
            notes = res.unique().scalars().all()

            count_stmt = select(func.count(Note.id)).where(
                Note.user_id == user_id,
                Note.tags.any(id=tag.id),
            )
            total_count_res = await session.execute(count_stmt)

            note_vos = [NoteVO(**row_to_dict(note)) for note in notes]

            return total_count_res.scalar_one(), note_vos
