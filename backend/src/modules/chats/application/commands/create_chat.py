from dataclasses import dataclass
from uuid import UUID

from src.core.event_bus import EventBus
from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.chats.application.realtime import join_members_to_chat_room
from src.modules.chats.domain.entities.chat import Chat
from src.modules.chats.domain.entities.dtos import (
    ChatCreate,
    ChatCreateData,
    MemberCreate,
)
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.events import ChatCreatedEvent
from src.modules.chats.domain.exceptions import SelfChatForbiddenError
from src.modules.chats.domain.repositories.chat_unit_of_work import (
    ChatUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class CreateChatCommand(Command):
    creator_id: UUID
    data: ChatCreateData


class CreateChatCommandHandler:
    def __init__(
        self,
        uow: ChatUnitOfWork,
        event_bus: EventBus,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._uow = uow
        self._event_bus = event_bus
        self._room_membership_updater = room_membership_updater

    async def _publish_events(self, chat: Chat) -> None:
        await self._event_bus.publish_many(chat.pull_events())

    async def handle(
        self, command: CreateChatCommand
    ) -> Result[Chat, SelfChatForbiddenError]:
        creator_id, data = command.creator_id, command.data
        if data.type == ChatType.private:
            return await self._get_or_create_private_chat(creator_id, data)
        return await self._create_group_chat(creator_id, data)

    async def _get_or_create_private_chat(
        self,
        creator_id: UUID,
        data: ChatCreateData,
    ) -> Result[Chat, SelfChatForbiddenError]:
        if creator_id == data.target_user_id:
            return Result.err(SelfChatForbiddenError())

        assert data.target_user_id

        existing_chat = await self._uow.chats.find_private_chat(
            user_a=creator_id,
            user_b=data.target_user_id,
        )
        if existing_chat:
            return Result.ok(existing_chat)

        chat = await self._uow.chats.create(ChatCreate(type=ChatType.private))
        chat.record_event(ChatCreatedEvent(chat_id=chat.id))

        member_ids = [creator_id, data.target_user_id]
        members = [
            MemberCreate(user_id=user_id, chat_id=chat.id) for user_id in member_ids
        ]

        await self._uow.members.add_members(members)
        await self._uow.commit()
        await self._publish_events(chat)
        await join_members_to_chat_room(
            self._room_membership_updater, chat.id, member_ids
        )

        return Result.ok(chat)

    async def _create_group_chat(
        self,
        creator_id: UUID,
        data: ChatCreateData,
    ) -> Result[Chat, SelfChatForbiddenError]:
        chat = await self._uow.chats.create(
            ChatCreate(
                owner_id=creator_id,
                type=ChatType.group,
                name=data.name,
                description=data.description,
            )
        )
        chat.record_event(ChatCreatedEvent(chat_id=chat.id))

        member_ids = list(data.member_ids) if data.member_ids else []
        members = [
            MemberCreate(
                user_id=user_id,
                chat_id=chat.id,
                role=ChatMemberRole.member,
            )
            for user_id in member_ids
        ]
        member_ids.append(creator_id)

        members.append(
            MemberCreate(
                user_id=creator_id,
                chat_id=chat.id,
                role=ChatMemberRole.owner,
            )
        )

        await self._uow.members.add_members(members)
        await self._uow.commit()
        await self._publish_events(chat)
        await join_members_to_chat_room(
            self._room_membership_updater, chat.id, member_ids
        )

        return Result.ok(chat)
