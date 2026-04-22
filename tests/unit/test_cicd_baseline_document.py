from pathlib import Path
import unittest


class CicdBaselineDocumentTest(unittest.TestCase):
    def test_cicd_baseline_document_carries_core_governance_sections(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "cicd_baseline.md").read_text()

        self.assertIn("## CI/CD 阶段模型", contents)
        self.assertIn("### 校验阶段", contents)
        self.assertIn("### 构建阶段", contents)
        self.assertIn("### 受控部署阶段", contents)
        self.assertIn("## 默认 CI 门禁", contents)
        self.assertIn("## 可发布制品", contents)
        self.assertIn("## 受控部署边界", contents)
        self.assertIn("### 最小发布后验证", contents)
        self.assertIn("### 回滚入口", contents)

    def test_cicd_baseline_document_marks_all_default_governance_gates_as_blocking(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "cicd_baseline.md").read_text()

        self.assertIn("文档一致性校验必须作为默认阻断项处理", contents)
        self.assertIn("依赖/安全最低门禁必须作为默认阻断项处理", contents)

    def test_cicd_baseline_document_keeps_releasable_artifact_platform_neutral(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "cicd_baseline.md").read_text()

        self.assertIn("容器镜像仅作为优先兼容的制品形式", contents)
        self.assertIn("可与发布记录、验证结果和回滚入口关联", contents)
        self.assertIn("不预设 GitHub Actions、GitLab CI、Jenkins 或其他平台实现已经存在", contents)

    def test_cicd_baseline_document_limits_cd_scope_to_controlled_deployment(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "cicd_baseline.md").read_text()

        self.assertIn("不扩展到多环境晋升或复杂发布编排", contents)
        self.assertIn("部署触发条件", contents)
        self.assertIn("目标环境准入条件", contents)
        self.assertIn("回滚入口", contents)

    def test_release_document_keeps_release_validation_and_rollback_scope(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "release_change_and_rollback.md").read_text()

        self.assertIn("本文负责发布控制、发布后验证与回滚原则的专题基线", contents)
        self.assertIn("CI/CD 负责提供平台中立的阶段边界、默认门禁与受控部署入口", contents)

    def test_security_document_links_minimum_security_gate_to_default_ci(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "security_baseline.md").read_text()

        self.assertIn("依赖/安全最低门禁属于默认 CI 门禁", contents)
        self.assertIn("不绑定特定平台语法或供应商能力", contents)

    def test_deployment_document_links_environment_admission_to_controlled_deployment(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "deployment_environment_baseline.md").read_text()

        self.assertIn("目标环境准入属于受控部署的一部分", contents)
        self.assertIn("而不是扩展为多环境晋升编排", contents)


if __name__ == "__main__":
    unittest.main()
