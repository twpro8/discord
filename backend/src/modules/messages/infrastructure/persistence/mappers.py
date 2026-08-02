from src.modules.messages.domain.entities.message import Message
from src.modules.messages.infrastructure.persistence.models import MessageOrm


class MessageDataMapper:
    @staticmethod
    def to_entity(model: MessageOrm) -> Message:
        return Message(
            id=model.id,
            sender_id=model.sender_id,
            chat_id=model.chat_id,
            channel_id=model.channel_id,
            body=model.body,
            sequence=model.sequence,
            parent_id=model.parent_id,
            is_edited=model.is_edited,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
