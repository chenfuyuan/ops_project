"""大纲节点 HTTP 接口。

本模块只负责 FastAPI 请求/响应模型映射和边界错误转换，
业务规则由注入的 outline service 处理。
"""

import logging
from collections.abc import Callable
from typing import Protocol
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.capabilities.ai_gateway import AiGatewayError

from app.business.novel_generate.nodes.outline.dto import (
    ChapterSummaryResponse,
    CreateSeedCommand,
    OutlineResponse,
    SeedResponse,
    SkeletonResponse,
    SkeletonVolumeResponse,
    UpdateChapterCommand,
    UpdateVolumeCommand,
)
from app.business.novel_generate.nodes.outline.entities import (
    ChapterSummary,
    Outline,
    Seed,
    Skeleton,
    SkeletonVolume,
)


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class UpdateVolumeBody(BaseModel):
    """HTTP PATCH body for editing a skeleton volume without exposing service internals."""

    title: str | None = None
    turning_point: str | None = None


class UpdateChapterBody(BaseModel):
    """HTTP PATCH body for editing a chapter summary without replacing the whole outline."""

    title: str | None = None
    summary: str | None = None


class OutlineHttpService(Protocol):
    """HTTP 层调用的大纲业务入口，具体依赖由 bootstrap 注入。"""

    def create_seed(self, command: CreateSeedCommand) -> Seed: ...

    def get_seed(self, seed_id: UUID) -> Seed: ...

    def generate_skeleton(self, seed_id: UUID) -> Skeleton: ...

    def get_skeleton(self, skeleton_id: UUID) -> Skeleton: ...

    def update_volume(self, command: UpdateVolumeCommand) -> SkeletonVolume: ...

    def confirm_skeleton(self, skeleton_id: UUID) -> Skeleton: ...

    def expand_volume(self, skeleton_id: UUID, volume_id: UUID) -> list[ChapterSummary]: ...

    def update_chapter(self, command: UpdateChapterCommand) -> ChapterSummary: ...

    def get_outline(self, seed_id: UUID) -> Outline: ...


class UnavailableOutlineService:
    """未装配 outline service 时的安全占位实现，让路由稳定返回 503。"""

    def create_seed(self, command: CreateSeedCommand) -> Seed:
        """创建种子不可用时抛出稳定运行时错误。"""
        raise RuntimeError("outline service is not configured.")

    def get_seed(self, seed_id: UUID) -> Seed:
        """读取种子不可用时抛出稳定运行时错误。"""
        raise RuntimeError("outline service is not configured.")

    def generate_skeleton(self, seed_id: UUID) -> Skeleton:
        """生成骨架不可用时抛出稳定运行时错误。"""
        raise RuntimeError("outline service is not configured.")

    def get_skeleton(self, skeleton_id: UUID) -> Skeleton:
        """读取骨架不可用时抛出稳定运行时错误。"""
        raise RuntimeError("outline service is not configured.")

    def update_volume(self, command: UpdateVolumeCommand) -> SkeletonVolume:
        """编辑骨架卷不可用时抛出稳定运行时错误。"""
        raise RuntimeError("outline service is not configured.")

    def confirm_skeleton(self, skeleton_id: UUID) -> Skeleton:
        """确认骨架不可用时抛出稳定运行时错误。"""
        raise RuntimeError("outline service is not configured.")

    def expand_volume(self, skeleton_id: UUID, volume_id: UUID) -> list[ChapterSummary]:
        """展开章节不可用时抛出稳定运行时错误。"""
        raise RuntimeError("outline service is not configured.")

    def update_chapter(self, command: UpdateChapterCommand) -> ChapterSummary:
        """编辑章节摘要不可用时抛出稳定运行时错误。"""
        raise RuntimeError("outline service is not configured.")

    def get_outline(self, seed_id: UUID) -> Outline:
        """读取完整大纲不可用时抛出稳定运行时错误。"""
        raise RuntimeError("outline service is not configured.")


def create_outline_router(service: OutlineHttpService) -> APIRouter:
    """创建大纲 HTTP router，依赖由 bootstrap 注入，路由层只做协议适配。"""
    router = APIRouter(prefix="/api/outlines")

    @router.post("/seeds", response_model=SeedResponse)
    def create_seed(command: CreateSeedCommand) -> SeedResponse:
        route = "create_seed"
        _log_request_received(route)
        try:
            response = _seed_response(service.create_seed(command))
            _log_request_completed(route, 200, seed_id=response.id)
            return response
        except RuntimeError as exc:
            _log_request_failed(route, 503, exc)
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ValueError as exc:
            _log_request_failed(route, 400, exc)
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/seeds/{seed_id}", response_model=SeedResponse)
    def get_seed(seed_id: UUID) -> SeedResponse:
        return _call_or_http_error(
            "get_seed",
            lambda: _seed_response(service.get_seed(seed_id)),
            seed_id=seed_id,
        )

    @router.post("/seeds/{seed_id}/skeleton", response_model=SkeletonResponse)
    def generate_skeleton(seed_id: UUID) -> SkeletonResponse:
        return _call_or_http_error(
            "generate_skeleton",
            lambda: _skeleton_response(service.generate_skeleton(seed_id)),
            seed_id=seed_id,
        )

    @router.get("/skeletons/{skeleton_id}", response_model=SkeletonResponse)
    def get_skeleton(skeleton_id: UUID) -> SkeletonResponse:
        return _call_or_http_error(
            "get_skeleton",
            lambda: _skeleton_response(service.get_skeleton(skeleton_id)),
            skeleton_id=skeleton_id,
        )

    @router.patch(
        "/skeletons/volumes/{volume_id}", response_model=SkeletonVolumeResponse
    )
    def update_volume(volume_id: UUID, body: UpdateVolumeBody) -> SkeletonVolumeResponse:
        return _call_or_http_error(
            "update_volume",
            lambda: _volume_response(
                service.update_volume(
                    UpdateVolumeCommand(
                        volume_id=volume_id,
                        title=body.title,
                        turning_point=body.turning_point,
                    )
                )
            ),
            volume_id=volume_id,
        )

    @router.post("/skeletons/{skeleton_id}/confirm", response_model=SkeletonResponse)
    def confirm_skeleton(skeleton_id: UUID) -> SkeletonResponse:
        return _call_or_http_error(
            "confirm_skeleton",
            lambda: _skeleton_response(service.confirm_skeleton(skeleton_id)),
            skeleton_id=skeleton_id,
        )

    @router.post(
        "/skeletons/{skeleton_id}/expand/{volume_id}",
        response_model=list[ChapterSummaryResponse],
    )
    def expand_volume(skeleton_id: UUID, volume_id: UUID) -> list[ChapterSummaryResponse]:
        return _call_or_http_error(
            "expand_volume",
            lambda: [
                _chapter_response(chapter)
                for chapter in service.expand_volume(skeleton_id, volume_id)
            ],
            skeleton_id=skeleton_id,
            volume_id=volume_id,
        )

    @router.patch("/chapters/{chapter_id}", response_model=ChapterSummaryResponse)
    def update_chapter(
        chapter_id: UUID, body: UpdateChapterBody
    ) -> ChapterSummaryResponse:
        return _call_or_http_error(
            "update_chapter",
            lambda: _chapter_response(
                service.update_chapter(
                    UpdateChapterCommand(
                        chapter_id=chapter_id,
                        title=body.title,
                        summary=body.summary,
                    )
                )
            ),
            chapter_id=chapter_id,
        )

    @router.get("/seeds/{seed_id}/outline", response_model=OutlineResponse)
    def get_outline(seed_id: UUID) -> OutlineResponse:
        return _call_or_http_error(
            "get_outline",
            lambda: _outline_response(service.get_outline(seed_id)),
            seed_id=seed_id,
        )

    return router


def _call_or_http_error(route: str, action: Callable[[], object], **context):
    """执行路由动作并把业务边界错误转换为 HTTP 状态码。

    查询、更新、确认和展开路径中的 ValueError 表示目标资源或状态不存在，
    因此统一映射为 404；创建 seed 的输入校验错误在 endpoint 内映射为 400。
    """
    _log_request_received(route, **context)
    try:
        response = action()
        _log_request_completed(route, 200, **context)
        return response
    except AiGatewayError as exc:
        _log_request_failed(route, 503, exc, **context)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        _log_request_failed(route, 503, exc, **context)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        _log_request_failed(route, 404, exc, **context)
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _log_request_received(route: str, **context) -> None:
    logger.info(
        "outline_http_request_received",
        extra={"route": route, **_safe_log_context(context)},
    )


def _log_request_completed(route: str, status_code: int, **context) -> None:
    logger.info(
        "outline_http_request_completed",
        extra={
            "route": route,
            "status_code": status_code,
            **_safe_log_context(context),
        },
    )


def _log_request_failed(route: str, status_code: int, exc: Exception, **context) -> None:
    event = (
        "outline_http_service_unavailable"
        if status_code == 503 and isinstance(exc, RuntimeError)
        else "outline_http_request_failed"
    )
    logger.warning(
        event,
        extra={
            "route": route,
            "status_code": status_code,
            "error_type": type(exc).__name__,
            **_safe_log_context(context),
        },
    )


def _safe_log_context(context: dict) -> dict[str, str]:
    allowed_keys = {"seed_id", "skeleton_id", "volume_id", "chapter_id"}
    return {
        key: str(value)
        for key, value in context.items()
        if key in allowed_keys and value is not None
    }


def _seed_response(seed: Seed) -> SeedResponse:
    return SeedResponse(
        id=seed.id,
        title=seed.title,
        genre=seed.genre,
        protagonist=seed.protagonist,
        core_conflict=seed.core_conflict,
        story_direction=seed.story_direction,
        additional_notes=seed.additional_notes,
    )


def _volume_response(volume: SkeletonVolume) -> SkeletonVolumeResponse:
    if volume.skeleton_id is None:
        raise ValueError("骨架卷缺少骨架 ID")
    return SkeletonVolumeResponse(
        id=volume.id,
        skeleton_id=volume.skeleton_id,
        sequence=volume.sequence,
        title=volume.title,
        turning_point=volume.turning_point,
    )


def _skeleton_response(skeleton: Skeleton) -> SkeletonResponse:
    return SkeletonResponse(
        id=skeleton.id,
        seed_id=skeleton.seed_id,
        status=skeleton.status.value,
        volumes=[_volume_response(volume) for volume in skeleton.volumes],
    )


def _chapter_response(chapter: ChapterSummary) -> ChapterSummaryResponse:
    return ChapterSummaryResponse(
        id=chapter.id,
        volume_id=chapter.volume_id,
        sequence=chapter.sequence,
        title=chapter.title,
        summary=chapter.summary,
        is_stale=chapter.is_stale,
    )


def _outline_response(outline: Outline) -> OutlineResponse:
    return OutlineResponse(
        seed=_seed_response(outline.seed),
        skeleton=_skeleton_response(outline.skeleton),
        chapters_by_volume={
            volume_id: [_chapter_response(chapter) for chapter in chapters]
            for volume_id, chapters in outline.chapters_by_volume.items()
        },
        status=outline.status.value,
    )
