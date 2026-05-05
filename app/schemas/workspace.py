import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.workspace import WorkspaceRole


class WorkspaceCreate(BaseModel):
    """Payload for creating a new workspace."""

    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(
        default=None,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        max_length=255,
        description="URL-friendly identifier. Auto-generated from name if omitted.",
    )


class WorkspaceMemberResponse(BaseModel):
    """A single workspace member with their role."""

    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    role: WorkspaceRole
    created_at: datetime


class WorkspaceResponse(BaseModel):
    """Workspace summary — used in list responses and after creation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime


class WorkspaceDetailResponse(WorkspaceResponse):
    """Workspace with full member list — used in detail responses."""

    members: list[WorkspaceMemberResponse]


class MemberInvite(BaseModel):
    """Payload for adding a member to a workspace."""

    user_id: uuid.UUID
    role: WorkspaceRole = WorkspaceRole.member


class MemberRoleUpdate(BaseModel):
    """Payload for changing a member's role."""

    role: WorkspaceRole
