from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import (
    CacheDep,
    RoomMembershipUpdaterDep,
    SessionDep,
    TransactionDep,
)
from src.modules.chats.adapters.persistence.chat_member_repository_impl import (
    ChatMemberRepositoryImpl,
)
from src.modules.chats.adapters.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.modules.chats.usecases.add_member import AddMemberUseCase
from src.modules.chats.usecases.create_chat import CreateChatUseCase
from src.modules.chats.usecases.get_chat_details import GetChatDetailsUseCase
from src.modules.chats.usecases.get_chats import GetChatsUseCase
from src.modules.chats.usecases.leave_chat import LeaveChatUseCase
from src.modules.chats.usecases.list_members import ListMembersUseCase
from src.modules.chats.usecases.mark_chat_as_read import MarkChatAsReadUseCase
from src.modules.chats.usecases.remove_member import RemoveMemberUseCase
from src.modules.chats.usecases.update_chat import UpdateChatUseCase
from src.modules.users.public.facade import UsersFacade, build_users_facade


def get_chat_repository(session: SessionDep) -> ChatRepository:
    return ChatRepositoryImpl(session)


def get_chat_member_repository(session: SessionDep) -> ChatMemberRepository:
    return ChatMemberRepositoryImpl(session)


def get_users_facade(session: SessionDep, cache: CacheDep) -> UsersFacade:
    return build_users_facade(session, cache)


ChatRepositoryDep = Annotated[ChatRepository, Depends(get_chat_repository)]
ChatMemberRepositoryDep = Annotated[
    ChatMemberRepository, Depends(get_chat_member_repository)
]
UsersFacadeDep = Annotated[UsersFacade, Depends(get_users_facade)]


async def get_create_chat_use_case(
    tx: TransactionDep,
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> CreateChatUseCase:
    return CreateChatUseCase(
        tx, chat_repository, chat_member_repository, room_membership_updater
    )


async def get_update_chat_use_case(
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
    _tx: TransactionDep,
) -> UpdateChatUseCase:
    return UpdateChatUseCase(chat_repository, chat_member_repository)


async def get_add_member_use_case(
    tx: TransactionDep,
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
    users_facade: UsersFacadeDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> AddMemberUseCase:
    return AddMemberUseCase(
        tx,
        chat_repository,
        chat_member_repository,
        users_facade,
        room_membership_updater,
    )


async def get_remove_member_use_case(
    tx: TransactionDep,
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> RemoveMemberUseCase:
    return RemoveMemberUseCase(
        tx, chat_repository, chat_member_repository, room_membership_updater
    )


async def get_leave_chat_use_case(
    tx: TransactionDep,
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> LeaveChatUseCase:
    return LeaveChatUseCase(
        tx, chat_repository, chat_member_repository, room_membership_updater
    )


async def get_mark_chat_as_read_use_case(
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
    _tx: TransactionDep,
) -> MarkChatAsReadUseCase:
    return MarkChatAsReadUseCase(chat_repository, chat_member_repository)


async def get_get_chats_use_case(
    chat_repository: ChatRepositoryDep,
) -> GetChatsUseCase:
    return GetChatsUseCase(chat_repository)


async def get_get_chat_details_use_case(
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
) -> GetChatDetailsUseCase:
    return GetChatDetailsUseCase(chat_repository, chat_member_repository)


async def get_list_members_use_case(
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
) -> ListMembersUseCase:
    return ListMembersUseCase(chat_repository, chat_member_repository)


CreateChatUseCaseDep = Annotated[CreateChatUseCase, Depends(get_create_chat_use_case)]
UpdateChatUseCaseDep = Annotated[UpdateChatUseCase, Depends(get_update_chat_use_case)]
AddMemberUseCaseDep = Annotated[AddMemberUseCase, Depends(get_add_member_use_case)]
RemoveMemberUseCaseDep = Annotated[
    RemoveMemberUseCase, Depends(get_remove_member_use_case)
]
LeaveChatUseCaseDep = Annotated[LeaveChatUseCase, Depends(get_leave_chat_use_case)]
MarkChatAsReadUseCaseDep = Annotated[
    MarkChatAsReadUseCase, Depends(get_mark_chat_as_read_use_case)
]
GetChatsUseCaseDep = Annotated[GetChatsUseCase, Depends(get_get_chats_use_case)]
GetChatDetailsUseCaseDep = Annotated[
    GetChatDetailsUseCase, Depends(get_get_chat_details_use_case)
]
ListMembersUseCaseDep = Annotated[
    ListMembersUseCase, Depends(get_list_members_use_case)
]
