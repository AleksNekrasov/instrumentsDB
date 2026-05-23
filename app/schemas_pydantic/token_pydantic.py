from pydantic import BaseModel, Field, ConfigDict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AccessTokenRequest(BaseModel):
    access_token: str