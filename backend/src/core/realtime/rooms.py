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


def server_room(server_id: UUID) -> str:
    """A server's room — the publish target for server-scoped events
    (currently: presence fan-out to co-members). Joined at server
    create/join time (see servers' Create/JoinServer command handlers)
    and lazily on view (see servers.application.queries.
    get_server_where_user_member), mirroring chat_room's join pattern.
    """
    return f"server:{server_id}"


def connection_room(connection_id: UUID) -> str:
    """Every connection's own private room, joined once at connect time
    (see api/v1/ws.py) — the finest-grained delivery target, for events
    that must reach exactly one open socket (e.g. call signaling relayed
    only to the specific tab that answered a call) rather than every
    connection for a user (user_room) or every member of a chat
    (chat_room). The server always knows the relevant connection_id for
    free from ConnectionManager.serve()'s reader loop, so callers never
    need a client to self-report one.
    """
    return f"connection:{connection_id}"
