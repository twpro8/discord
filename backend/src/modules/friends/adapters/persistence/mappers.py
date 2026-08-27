from src.modules.friends.adapters.persistence.models import FriendOrm
from src.modules.friends.domain.entities.friend_request import FriendRequest


class FriendRequestDataMapper:
    @staticmethod
    def to_entity(model: FriendOrm) -> FriendRequest:
        return FriendRequest(
            id=model.id,
            user_id=model.user_id,
            target_user_id=model.target_user_id,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
