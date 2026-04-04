import unittest

from shared.static_pool import (
    classify_l5_candidate,
    evaluate_promotion_gate,
    is_placeholder,
    normalize_review_status,
    should_allow_frozen_text_as_input,
)


def _base_main_row() -> dict:
    return {
        "account_id": "acc_demo",
        "account_canonical_name": "示例公司",
        "primary_track": "零售消费",
        "persona_tag": "retail_high_sku_brand",
        "公司产品与服务概述": "主营护肤和彩妆产品，并通过线上线下渠道销售。",
        "商业模式概述": "以品牌经营和全渠道销售为主。",
        "admission_reason_summary": "已确认品牌消费品属性，且多渠道经营复杂度成立。",
        "validation_gap": "待确认直营网/经销比例。",
        "review_status": "active",
    }


def _evidence() -> list[dict]:
    return [
        {
            "source_locator": "官网-关于我们",
            "source_type": "official_website",
            "evidence_strength": "A",
            "summary": "官网可确认品牌消费品属性。",
        },
        {
            "source_locator": "2025 年报",
            "source_type": "annual_report",
            "evidence_strength": "S",
            "summary": "年报可确认商业模式与渠道结构。",
        },
    ]


class ValidatorTests(unittest.TestCase):
    def test_is_placeholder(self) -> None:
        self.assertTrue(is_placeholder("待补充"))
        self.assertFalse(is_placeholder("主营护肤和彩妆产品"))

    def test_normalize_review_status(self) -> None:
        self.assertEqual(normalize_review_status("queued"), "pending_review")
        self.assertEqual(normalize_review_status("active"), "active")

    def test_classify_l5_candidate_formal(self) -> None:
        result = classify_l5_candidate(_base_main_row(), _evidence())
        self.assertTrue(result.is_formal_l5_candidate)
        self.assertEqual(result.review_status, "active")

    def test_classify_l5_candidate_observation(self) -> None:
        row = _base_main_row()
        row["商业模式概述"] = "以品牌消费品经营为主，依赖线上线下或多渠道协同。"
        result = classify_l5_candidate(row, _evidence()[:1])
        self.assertFalse(result.is_formal_l5_candidate)
        self.assertEqual(result.review_status, "pending_review")

    def test_evaluate_promotion_gate_block(self) -> None:
        row = _base_main_row()
        row["validation_gap"] = "待进一步完善"
        result = evaluate_promotion_gate(row, {"validation_gap": "待进一步完善"}, _evidence()[:1], [])
        self.assertEqual(result.decision, "block")

    def test_should_allow_frozen_text_as_input(self) -> None:
        self.assertTrue(should_allow_frozen_text_as_input("abstract_knowledge"))
        self.assertFalse(should_allow_frozen_text_as_input("legacy_archive_body"))


if __name__ == "__main__":
    unittest.main()
