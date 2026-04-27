"""大纲应用层外部能力端口。

端口用业务语言描述应用层需要的 AI 能力，避免 use case 直接依赖 capability、SDK
或 provider 细节。具体 prompt、profile、schema 与错误转换由 infrastructure adapter
负责。
"""

from typing import Protocol

from app.business.novel_generate.nodes.outline.domain.models import (
    ChapterSummary,
    Seed,
    Skeleton,
    SkeletonVolume,
)


class OutlineAiPort(Protocol):
    """大纲节点需要的 AI 生成能力。"""

    def generate_skeleton(self, seed: Seed) -> list[SkeletonVolume]:
        """根据创作种子生成骨架卷列表。

        实现方可以调用 AI gateway 或其他 provider，但不得把 provider 响应结构泄漏
        给应用层；返回值必须已经转换为领域模型。
        """
        ...

    def expand_volume(
        self, seed: Seed, skeleton: Skeleton, volume: SkeletonVolume
    ) -> list[ChapterSummary]:
        """根据已确认骨架展开某个卷的章节摘要。

        seed、skeleton 与 volume 可能包含作者创作内容，端口实现记录日志时只能使用
        ID、计数和阶段信息等安全摘要。
        """
        ...
