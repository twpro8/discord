from collections.abc import AsyncGenerator
from contextlib import aclosing
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import (
    CacheDep,
    EventBusDep,
    RoomMembershipUpdaterDep,
    SessionDep,
)
from src.modules.chats.adapters.chat_unit_of_work_impl import ChatUnitOfWorkImpl
from src.modules.chats.adapters.persistence.chat_member_repository_impl import (
    ChatMemberRepositoryImpl,
)
from src.modules.chats.adapters.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork
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


async def get_chat_unit_of_work(session: SessionDep) -> AsyncGenerator[ChatUnitOfWork]:
    chat_repository = ChatRepositoryImpl(session)
    chat_member_repository = ChatMemberRepositoryImpl(session)
    async with ChatUnitOfWorkImpl(
        session=session,
        chat_repository=chat_repository,
        chat_member_repository=chat_member_repository,
    ) as uow:
        yield uow


async def get_users_facade(
    session: SessionDep, cache: CacheDep, event_bus: EventBusDep
) -> AsyncGenerator[UsersFacade]:
    async with aclosing(build_users_facade(session, cache, event_bus)) as facades:
        async for facade in facades:
            yield facade


ChatUnitOfWorkDep = Annotated[ChatUnitOfWork, Depends(get_chat_unit_of_work)]
UsersFacadeDep = Annotated[UsersFacade, Depends(get_users_facade)]


async def get_create_chat_use_case(
    uow: ChatUnitOfWorkDep,
    event_bus: EventBusDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> CreateChatUseCase:
    return CreateChatUseCase(uow, event_bus, room_membership_updater)


async def get_update_chat_use_case(uow: ChatUnitOfWorkDep) -> UpdateChatUseCase:
    return UpdateChatUseCase(uow)


async def get_add_member_use_case(
    uow: ChatUnitOfWorkDep,
    users_facade: UsersFacadeDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> AddMemberUseCase:
    return AddMemberUseCase(uow, users_facade, room_membership_updater)


async def get_remove_member_use_case(
    uow: ChatUnitOfWorkDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> RemoveMemberUseCase:
    return RemoveMemberUseCase(uow, room_membership_updater)


async def get_leave_chat_use_case(
    uow: ChatUnitOfWorkDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> LeaveChatUseCase:
    return LeaveChatUseCase(uow, room_membership_updater)


async def get_mark_chat_as_read_use_case(
    uow: ChatUnitOfWorkDep,
) -> MarkChatAsReadUseCase:
    return MarkChatAsReadUseCase(uow)


async def get_get_chats_use_case(uow: ChatUnitOfWorkDep) -> GetChatsUseCase:
    return GetChatsUseCase(uow.chats)


async def get_get_chat_details_use_case(
    uow: ChatUnitOfWorkDep,
) -> GetChatDetailsUseCase:
    return GetChatDetailsUseCase(uow.chats, uow.members)


async def get_list_members_use_case(uow: ChatUnitOfWorkDep) -> ListMembersUseCase:
    return ListMembersUseCase(uow.chats, uow.members)


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
