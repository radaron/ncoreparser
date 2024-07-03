from datetime import datetime
from typing import Dict
from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class Permissions(BaseModel):
    invite: bool


class CategorySettings(BaseModel):
    list: bool
    show: bool


class Settings(BaseModel):
    categories: Dict[str, CategorySettings]


class User(BaseModel):
    id: int
    email_confirmed: bool
    display_name: str
    created_at: datetime
    downloaded: int
    uploaded: int
    tracker_key: str
    avatar: str
    permissions: Permissions
    rss_key: str
    api_key: str
    getting_started: bool
    settings: Settings

    class Config:
        alias_generator = to_camel


class Auth(BaseModel):
    user: User
