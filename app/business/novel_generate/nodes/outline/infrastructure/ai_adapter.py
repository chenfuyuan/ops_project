"""大纲节点的 AI port 适配器。

本模块把业务层的大纲生成需求翻译为 AI gateway 的中性结构化请求，
并把结构化响应映射回业务实体，避免业务核心依赖 provider 细节。
"""

import logging
from typing import Any

from app.business.novel_generate.nodes.outline.entities import (
    ChapterSummary,
    Seed,
    Skeleton,
    SkeletonVolume,
)
from app.business.novel_generate.nodes.outline.ports import OutlineAiPort
from app.capabilities.ai_gateway import (
    AiGatewayError,
    AiGatewayFacade,
    AiGatewayMessage,
    AiGatewayRequest,
    CapabilityProfileName,
    MessageRole,
    OutputMode,
    StructuredOutputConstraint,
)


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# AI gateway 结构化输出契约，只约束生成响应形状，不替代业务实体校验。
SKELETON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "volumes": {
            "type": "array",
            "minItems": 3,
            "maxItems": 5,
            "items": {
                "type": "object",
                "properties": {
                    "sequence": {"type": "integer", "minimum": 1},
                    "title": {"type": "string", "minLength": 1},
                    "turning_point": {"type": "string", "minLength": 1},
                },
                "required": ["sequence", "title", "turning_point"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["volumes"],
    "additionalProperties": False,
}

# 章节展开响应只保留后续编辑需要的章节序号、标题和摘要。
CHAPTER_EXPANSION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "chapters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sequence": {"type": "integer", "minimum": 1},
                    "title": {"type": "string", "minLength": 1},
                    "summary": {"type": "string", "minLength": 1},
                },
                "required": ["sequence", "title", "summary"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["chapters"],
    "additionalProperties": False,
}


class OutlineAiAdapter(OutlineAiPort):
    """实现大纲 AI port，屏蔽 AI gateway 请求格式和 profile 选择。"""

    def __init__(self, gateway: AiGatewayFacade) -> None:
        self._gateway = gateway

    def generate_skeleton(self, seed: Seed) -> list[SkeletonVolume]:
        """基于结构化种子生成 3-5 个骨架卷，不在日志中暴露创作内容。"""
        profile = CapabilityProfileName("outline-skeleton")
        logger.info(
            "outline_ai_skeleton_request_started",
            extra={
                "seed_id": str(seed.id),
                "profile": str(profile),
                "schema_name": "outline_skeleton",
            },
        )
        try:
            response = self._gateway.generate(
                AiGatewayRequest(
                    capability_profile=profile,
                    output_mode=OutputMode.STRUCTURED,
                    structured_output=StructuredOutputConstraint(
                        name="outline_skeleton",
                        schema=SKELETON_SCHEMA,
                    ),
                    messages=[
                        AiGatewayMessage(
                            role=MessageRole.SYSTEM,
                            content="你是小说大纲策划助手，只输出符合 JSON Schema 的骨架。",
                        ),
                        AiGatewayMessage(role=MessageRole.USER, content=self._seed_prompt(seed)),
                    ],
                )
            )
        except AiGatewayError as exc:
            logger.warning(
                "outline_ai_request_failed",
                extra={
                    "stage": "generate_skeleton",
                    "seed_id": str(seed.id),
                    "profile": str(profile),
                    "error_type": type(exc).__name__,
                },
            )
            raise
        content = response.structured_content or {}
        volumes = [
            SkeletonVolume(
                skeleton_id=None,
                sequence=int(item["sequence"]),
                title=str(item["title"]),
                turning_point=str(item["turning_point"]),
            )
            for item in content.get("volumes", [])
        ]
        logger.info(
            "outline_ai_skeleton_request_completed",
            extra={"seed_id": str(seed.id), "volume_count": len(volumes)},
        )
        return volumes

    def expand_volume(
        self, seed: Seed, skeleton: Skeleton, volume: SkeletonVolume
    ) -> list[ChapterSummary]:
        """基于种子、完整骨架和目标卷生成章节摘要，不泄露 prompt 或正文。"""
        profile = CapabilityProfileName("outline-chapter-expansion")
        logger.info(
            "outline_ai_volume_request_started",
            extra={
                "seed_id": str(seed.id),
                "skeleton_id": str(skeleton.id),
                "volume_id": str(volume.id),
                "profile": str(profile),
                "schema_name": "outline_chapter_expansion",
            },
        )
        try:
            response = self._gateway.generate(
                AiGatewayRequest(
                    capability_profile=profile,
                    output_mode=OutputMode.STRUCTURED,
                    structured_output=StructuredOutputConstraint(
                        name="outline_chapter_expansion",
                        schema=CHAPTER_EXPANSION_SCHEMA,
                    ),
                    messages=[
                        AiGatewayMessage(
                            role=MessageRole.SYSTEM,
                            content="你是小说章节规划助手，只输出符合 JSON Schema 的章节摘要。",
                        ),
                        AiGatewayMessage(
                            role=MessageRole.USER,
                            content=self._volume_prompt(seed, skeleton, volume),
                        ),
                    ],
                )
            )
        except AiGatewayError as exc:
            logger.warning(
                "outline_ai_request_failed",
                extra={
                    "stage": "expand_volume",
                    "seed_id": str(seed.id),
                    "skeleton_id": str(skeleton.id),
                    "volume_id": str(volume.id),
                    "profile": str(profile),
                    "error_type": type(exc).__name__,
                },
            )
            raise
        content = response.structured_content or {}
        chapters = [
            ChapterSummary(
                volume_id=volume.id,
                sequence=int(item["sequence"]),
                title=str(item["title"]),
                summary=str(item["summary"]),
            )
            for item in content.get("chapters", [])
        ]
        logger.info(
            "outline_ai_volume_request_completed",
            extra={
                "seed_id": str(seed.id),
                "skeleton_id": str(skeleton.id),
                "volume_id": str(volume.id),
                "chapter_count": len(chapters),
            },
        )
        return chapters

    def _seed_prompt(self, seed: Seed) -> str:
        """构造种子提示词；返回值含用户创作内容，禁止写入日志。"""
        return (
            f"标题：{seed.title}\n"
            f"题材：{seed.genre}\n"
            f"主角：{seed.protagonist}\n"
            f"核心冲突：{seed.core_conflict}\n"
            f"故事走向：{seed.story_direction}\n"
            f"补充说明：{seed.additional_notes or '无'}"
        )

    def _volume_prompt(self, seed: Seed, skeleton: Skeleton, volume: SkeletonVolume) -> str:
        """构造卷展开提示词；仅传给 AI gateway，不进入日志上下文。"""
        volume_lines = "\n".join(
            f"{item.sequence}. {item.title}：{item.turning_point}"
            for item in skeleton.volumes
        )
        return (
            f"{self._seed_prompt(seed)}\n\n"
            f"完整骨架：\n{volume_lines}\n\n"
            f"请展开第 {volume.sequence} 卷《{volume.title}》：{volume.turning_point}"
        )
