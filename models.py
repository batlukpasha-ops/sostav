from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    age: int = Field(ge=18)


class User(BaseModel):
    id: int
    name: str
    email: str
    age: int


class ProfileCreate(BaseModel):
    user_id: int = Field(gt=0)
    city: str = Field(min_length=1, max_length=100)
    bio: str = Field(min_length=1)


class Profile(BaseModel):
    id: int
    user_id: int
    city: str
    bio: str


class LikeCreate(BaseModel):
    from_user_id: int = Field(gt=0)
    to_user_id: int = Field(gt=0)


class Like(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int


class Match(BaseModel):
    id: int
    user1_id: int
    user2_id: int
