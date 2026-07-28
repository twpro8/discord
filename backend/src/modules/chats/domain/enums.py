from enum import StrEnum


class ChatType(StrEnum):
    private = "private"
    group = "group"


class ChatMemberRole(StrEnum):
    owner = "owner"
    member = "member"
