import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser
from app.core.db import get_db
from app.repositories.user import UserRepository
from app.repositories.workspace import WorkspaceRepository
from app.schemas.workspace import (
    MemberInvite,
    MemberRoleUpdate,
    WorkspaceCreate,
    WorkspaceDetailResponse,
    WorkspaceMemberResponse,
    WorkspaceResponse,
)
from app.services.workspace import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def _get_workspace_service(session: SessionDep) -> WorkspaceService:
    return WorkspaceService(
        workspace_repo=WorkspaceRepository(session),
        user_repo=UserRepository(session),
    )


WorkspaceServiceDep = Annotated[WorkspaceService, Depends(_get_workspace_service)]


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    data: WorkspaceCreate,
    service: WorkspaceServiceDep,
    current_user: CurrentUser,
) -> WorkspaceResponse:
    """Create a new workspace. The creator becomes its owner."""
    workspace = await service.create_workspace(data, creator_id=current_user.id)
    return WorkspaceResponse.model_validate(workspace)


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    service: WorkspaceServiceDep,
    current_user: CurrentUser,
) -> list[WorkspaceResponse]:
    """List all workspaces the current user belongs to."""
    workspaces = await service.get_user_workspaces(current_user.id)
    return [WorkspaceResponse.model_validate(w) for w in workspaces]


@router.get("/{slug}", response_model=WorkspaceDetailResponse)
async def get_workspace(
    slug: str,
    service: WorkspaceServiceDep,
    current_user: CurrentUser,
) -> WorkspaceDetailResponse:
    """Get workspace details including the full member list."""
    workspace = await service.get_workspace(slug, requesting_user_id=current_user.id)
    return WorkspaceDetailResponse.model_validate(workspace)


@router.post(
    "/{slug}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_member(
    slug: str,
    data: MemberInvite,
    service: WorkspaceServiceDep,
    current_user: CurrentUser,
) -> WorkspaceMemberResponse:
    """Add a user to the workspace. Requires admin or owner role."""
    member = await service.invite_member(slug, data, actor_id=current_user.id)
    return WorkspaceMemberResponse.model_validate(member)


@router.patch(
    "/{slug}/members/{user_id}",
    response_model=WorkspaceMemberResponse,
)
async def update_member_role(
    slug: str,
    user_id: uuid.UUID,
    data: MemberRoleUpdate,
    service: WorkspaceServiceDep,
    current_user: CurrentUser,
) -> WorkspaceMemberResponse:
    """Change a member's role. Requires owner role."""
    member = await service.update_member_role(
        slug, target_user_id=user_id, data=data, actor_id=current_user.id
    )
    return WorkspaceMemberResponse.model_validate(member)


@router.delete(
    "/{slug}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_member(
    slug: str,
    user_id: uuid.UUID,
    service: WorkspaceServiceDep,
    current_user: CurrentUser,
) -> None:
    """Remove a member from the workspace. Members can remove themselves."""
    await service.remove_member(slug, target_user_id=user_id, actor_id=current_user.id)
