from app.business.novel_generate.nodes.outline.facade import OutlineFacade


class OutlineNode:
    def __init__(self, facade: OutlineFacade) -> None:
        self._facade = facade
