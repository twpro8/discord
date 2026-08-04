from uuid import UUID


def user_room(user_id: UUID) -> str:
    """Permanent pseudo-room every connection for a user auto-joins on
    connect — the floor for delivery to that user regardless of any
    chat/channel room concept existing for a given event (see plan §3.3).
    """
    return f"user:{user_id}"


def chat_room(chat_id: UUID) -> str:
    """A chat's room — the single publish target for chat messages.
    Connections are joined to it two ways: at connect time, for chats the
    user is already active in (see api/v1/ws.py); and dynamically, when a
    chat is created or a member is added (see chats' Create/AddMember
    command handlers, via core.realtime.membership.
    DistributedRoomMembershipUpdater), so a connection that predates the
    chat's existence — on this instance or any other — still gets joined.
    """
    return f"chat:{chat_id}"
