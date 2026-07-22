from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True)]
uuid_pk = Annotated[
    UUID,
    mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    ),
]
str_128 = Annotated[str, mapped_column(String(128))]
str_255 = Annotated[str, mapped_column(String(255))]
str_512 = Annotated[str, mapped_column(String(512))]
str_1024 = Annotated[str, mapped_column(String(1024))]
timestamp = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    ),
]
