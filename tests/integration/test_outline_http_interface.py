import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.business.novel_generate.nodes.outline.entities import (
    ChapterSummary,
    Outline,
    OutlineStatus,
    Seed,
    Skeleton,
    SkeletonStatus,
    SkeletonVolume,
)
from app.capabilities.ai_gateway import ProviderTimeoutError
from app.interfaces.http.app import build_http_app


class FakeOutlineService:
    def __init__(self) -> None:
        self.seed = Seed(
            title="群星回声",
            genre="科幻",
            protagonist="失忆领航员",
            core_conflict="殖民舰队争夺唯一航道",
            story_direction="主角发现真相",
        )
        self.volume = SkeletonVolume(
            skeleton_id=None,
            sequence=1,
            title="开端",
            turning_point="发现航道",
        )
        self.skeleton = Skeleton(
            seed_id=self.seed.id,
            volumes=[self.volume],
            status=SkeletonStatus.DRAFT,
        )
        self.volume.skeleton_id = self.skeleton.id
        self.chapter = ChapterSummary(
            volume_id=self.volume.id,
            sequence=1,
            title="第一章",
            summary="启程",
        )

    def create_seed(self, command):
        self.received_seed_command = command
        return self.seed

    def get_seed(self, seed_id):
        return self.seed

    def generate_skeleton(self, seed_id):
        return self.skeleton

    def get_skeleton(self, skeleton_id):
        return self.skeleton

    def update_volume(self, command):
        self.volume.title = command.title
        self.volume.turning_point = command.turning_point
        return self.volume

    def confirm_skeleton(self, skeleton_id):
        self.skeleton.status = SkeletonStatus.CONFIRMED
        return self.skeleton

    def expand_volume(self, skeleton_id, volume_id):
        return [self.chapter]

    def update_chapter(self, command):
        self.chapter.title = command.title
        self.chapter.summary = command.summary
        return self.chapter

    def get_outline(self, seed_id):
        return Outline(
            seed=self.seed,
            skeleton=self.skeleton,
            chapters_by_volume={self.volume.id: [self.chapter]},
            status=OutlineStatus.COMPLETE,
        )


class OutlineHttpInterfaceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FakeOutlineService()
        self.client = TestClient(build_http_app(outline_service=self.service))

    def test_create_seed_endpoint_maps_request_to_service(self) -> None:
        response = self.client.post(
            "/api/outlines/seeds",
            json={
                "title": "群星回声",
                "genre": "科幻",
                "protagonist": "失忆领航员",
                "core_conflict": "殖民舰队争夺唯一航道",
                "story_direction": "主角发现真相",
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(str(self.service.seed.id), response.json()["id"])
        self.assertEqual("群星回声", self.service.received_seed_command.title)

    def test_missing_seed_field_returns_422(self) -> None:
        response = self.client.post(
            "/api/outlines/seeds",
            json={"title": "群星回声"},
        )

        self.assertEqual(422, response.status_code)

    def test_outline_endpoints_map_service_results(self) -> None:
        seed_id = self.service.seed.id
        skeleton_id = self.service.skeleton.id
        volume_id = self.service.volume.id
        chapter_id = self.service.chapter.id

        self.assertEqual(200, self.client.get(f"/api/outlines/seeds/{seed_id}").status_code)
        skeleton_response = self.client.post(
            f"/api/outlines/seeds/{seed_id}/skeleton"
        )
        self.assertEqual(200, skeleton_response.status_code)
        self.assertEqual("draft", skeleton_response.json()["status"])
        self.assertEqual(
            200, self.client.get(f"/api/outlines/skeletons/{skeleton_id}").status_code
        )
        volume_response = self.client.patch(
            f"/api/outlines/skeletons/volumes/{volume_id}",
            json={"title": "改写卷", "turning_point": "新转折"},
        )
        self.assertEqual("改写卷", volume_response.json()["title"])
        confirm_response = self.client.post(
            f"/api/outlines/skeletons/{skeleton_id}/confirm"
        )
        self.assertEqual("confirmed", confirm_response.json()["status"])
        expand_response = self.client.post(
            f"/api/outlines/skeletons/{skeleton_id}/expand/{volume_id}"
        )
        self.assertEqual("第一章", expand_response.json()[0]["title"])
        chapter_response = self.client.patch(
            f"/api/outlines/chapters/{chapter_id}",
            json={"title": "改写章", "summary": "改写摘要"},
        )
        self.assertEqual("改写章", chapter_response.json()["title"])
        outline_response = self.client.get(f"/api/outlines/seeds/{seed_id}/outline")
        self.assertEqual("complete", outline_response.json()["status"])

    def test_service_value_error_returns_404(self) -> None:
        class MissingService(FakeOutlineService):
            def get_seed(self, seed_id):
                raise ValueError("种子未找到")

        client = TestClient(build_http_app(outline_service=MissingService()))

        response = client.get(f"/api/outlines/seeds/{uuid4()}")

        self.assertEqual(404, response.status_code)
        self.assertEqual({"detail": "种子未找到"}, response.json())

    def test_provider_timeout_returns_503(self) -> None:
        class TimeoutService(FakeOutlineService):
            def generate_skeleton(self, seed_id):
                raise ProviderTimeoutError("AI provider HTTP call timed out")

        client = TestClient(build_http_app(outline_service=TimeoutService()))

        response = client.post(f"/api/outlines/seeds/{uuid4()}/skeleton")

        self.assertEqual(503, response.status_code)
        self.assertEqual(
            {"detail": "provider_timeout: AI provider HTTP call timed out"},
            response.json(),
        )


if __name__ == "__main__":
    unittest.main()
