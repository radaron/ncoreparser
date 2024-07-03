from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Settings(BaseModel):
    categories: bool


class Permission(BaseModel):
    invite: bool


class User(BaseModel):
    id: int
    email_confirmed: bool
    display_name: str
    createdAt: datetime
    downloaded: int
    uploaded: int
    tracker_key: str
    avatar: str
    permissions: Permission
    rss_key: str
    api_key: str
    getting_started: bool
    settings: Settings

    model_config = ConfigDict(
        alias_generator=to_camel
    )


external_data = {
    "id": 123,
    "emailConfirmed": True,
    "displayName": "John Doe",
    "createdAt": "0001-01-01T00:00:00Z",
}
user = User(**external_data)
print(user)
print(user.id)
