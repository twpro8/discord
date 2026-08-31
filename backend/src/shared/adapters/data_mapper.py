from typing import Protocol


class DataMapper[ModelT, EntityT](Protocol):
    @staticmethod
    def to_entity(model: ModelT) -> EntityT: ...

    @staticmethod
    def to_model(entity: EntityT) -> ModelT: ...
