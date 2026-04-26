import unittest

from app.business.novel_generate.nodes.outline.entities import Seed, Skeleton, SkeletonVolume
from app.business.novel_generate.nodes.outline.infrastructure.ai_adapter import OutlineAiAdapter
from app.capabilities.ai_gateway import AiGatewayResponse, OutputMode, TokenUsage


class FakeAiGatewayFacade:
    def __init__(self, structured_content) -> None:
        self.structured_content = structured_content
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        return AiGatewayResponse(
            output_mode=OutputMode.STRUCTURED,
            content=None,
            structured_content=self.structured_content,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
        )


class OutlineAiAdapterTest(unittest.TestCase):
    def test_generate_skeleton_uses_structured_mode_and_maps_volumes(self) -> None:
        gateway = FakeAiGatewayFacade(
            {
                "volumes": [
                    {"sequence": 1, "title": "开端", "turning_point": "发现航道"},
                    {"sequence": 2, "title": "终局", "turning_point": "关闭航道"},
                ]
            }
        )
        seed = Seed(
            title="群星回声",
            genre="科幻",
            protagonist="失忆领航员",
            core_conflict="殖民舰队争夺唯一航道",
            story_direction="主角发现真相",
        )
        adapter = OutlineAiAdapter(gateway)

        volumes = adapter.generate_skeleton(seed)

        self.assertEqual(OutputMode.STRUCTURED, gateway.requests[0].output_mode)
        self.assertEqual("outline-skeleton", gateway.requests[0].capability_profile)
        self.assertEqual("outline_skeleton", gateway.requests[0].structured_output.name)
        self.assertEqual(["开端", "终局"], [volume.title for volume in volumes])
        self.assertIsNone(volumes[0].skeleton_id)

    def test_expand_volume_uses_structured_mode_and_maps_chapters(self) -> None:
        gateway = FakeAiGatewayFacade(
            {
                "chapters": [
                    {"sequence": 1, "title": "第一章", "summary": "启程"},
                    {"sequence": 2, "title": "第二章", "summary": "遭遇"},
                ]
            }
        )
        seed = Seed(
            title="群星回声",
            genre="科幻",
            protagonist="失忆领航员",
            core_conflict="殖民舰队争夺唯一航道",
            story_direction="主角发现真相",
        )
        volume = SkeletonVolume(
            skeleton_id=None,
            sequence=1,
            title="开端",
            turning_point="发现航道",
        )
        skeleton = Skeleton(seed_id=seed.id, volumes=[volume])
        volume.skeleton_id = skeleton.id
        adapter = OutlineAiAdapter(gateway)

        chapters = adapter.expand_volume(seed, skeleton, volume)

        self.assertEqual(OutputMode.STRUCTURED, gateway.requests[0].output_mode)
        self.assertEqual("outline-chapter-expansion", gateway.requests[0].capability_profile)
        self.assertEqual("outline_chapter_expansion", gateway.requests[0].structured_output.name)
        self.assertEqual(["第一章", "第二章"], [chapter.title for chapter in chapters])
        self.assertEqual(volume.id, chapters[0].volume_id)


if __name__ == "__main__":
    unittest.main()
