"""大纲 workflow node 适配层。

当前 outline 能力主要通过 facade 暴露给外部入口；本类保留 workflow-facing 的
依赖注入位置，后续接入具体 workflow state 时应只负责 state 与 facade 入参/出参
之间的映射，不应下探到 use case、repository 或 infrastructure。
"""

from app.business.novel_generate.nodes.outline.facade import OutlineFacade


class OutlineNode:
    """持有 OutlineFacade 的 workflow 适配器占位实现。"""

    def __init__(self, facade: OutlineFacade) -> None:
        """由 bootstrap 注入 facade，避免 workflow 层自行装配业务依赖。"""
        self._facade = facade
