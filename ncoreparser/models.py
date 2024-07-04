from datetime import datetime
from typing import Dict, Optional, List
from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class PermissionsResponse(BaseModel):
    invite: bool


class CategorySettingsResponse(BaseModel):
    list: bool
    show: bool


class SettingsResponse(BaseModel):
    categories: Dict[str, CategorySettingsResponse]


class UserResponse(BaseModel):
    id: int
    email_confirmed: bool
    display_name: str
    created_at: datetime
    downloaded: int
    uploaded: int
    tracker_key: str
    token: str
    avatar: str
    permissions: PermissionsResponse
    rss_key: str
    api_key: str
    getting_started: bool
    settings: SettingsResponse

    class Config:
        alias_generator = to_camel


class AuthResponse(BaseModel):
    user: UserResponse


class MetaInfoResponse(BaseModel):
    root: str
    files: Optional[list] = None


class TorrentResponse(BaseModel):
    id: int
    release_name: str
    category: int
    created_at: datetime
    size: int
    downloaded: int
    seeders: int
    partial_seeders: int
    leechers: int
    verified: int
    metainfo: MetaInfoResponse

    class Config:
        alias_generator = to_camel


class TorrentSearchResult(BaseModel):
    hits: int
    took: int
    torrents: List[TorrentResponse]
