from __future__ import annotations

from datetime import datetime
from typing import Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel, EmailStr, Field, ValidationError


T = TypeVar("T", bound=BaseModel)


class ApiValidationError(BaseModel):
    status: str = "error"
    message: str = "Validation error"
    details: List[dict] = Field(default_factory=list)


def validate_json(model: Type[T], data: object) -> T:
    return model.model_validate(data)


def validation_error_payload(e: ValidationError) -> dict:
    return ApiValidationError(details=e.errors()).model_dump()


# ----- Common -----


class Pagination(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int


# ----- Users -----


class UserCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)


class UserUpdateIn(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=1, max_length=255)


class UserDeleteIn(BaseModel):
    password: str = Field(min_length=1, max_length=255)


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: Optional[str] = None


class UsersListOut(BaseModel):
    status: str = "success"
    count: int
    users: List[UserOut]


class UserSingleOut(BaseModel):
    status: str = "success"
    user: UserOut


class UserCreatedOut(BaseModel):
    status: str = "success"
    message: str = "User created successfully"
    user: UserOut


class UserUpdatedOut(BaseModel):
    status: str = "success"
    message: str = "User updated successfully"
    user: UserOut


class UserDeletedOut(BaseModel):
    status: str = "success"
    message: str = "User deleted successfully"


# ----- Projects -----


class ProjectOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    order: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    user_count: int


class ProjectsListOut(BaseModel):
    status: str = "success"
    count: int
    projects: List[ProjectOut]


class ProjectAddUserIn(BaseModel):
    email: EmailStr


class ProjectUserChangedOut(BaseModel):
    status: str = "success"
    message: str
    project: ProjectOut


# ----- Tasks -----


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    order: int
    project_id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TasksByProjectQuery(BaseModel):
    email: EmailStr
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)


class TasksByProjectOut(BaseModel):
    status: str = "success"
    project_id: int
    user_email: EmailStr
    pagination: Pagination
    tasks: List[TaskOut]
