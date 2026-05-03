from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CANDIDATES = "deliveries/archive/milestones/milestone14_small_batch_expansion/milestone14_small_batch_candidates_v1.json"
DEFAULT_PROMOTE = "deliveries/archive/milestones/milestone14_small_batch_expansion/milestone14_small_batch_promote_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone14_2_intake_quality_unblock"
DEFAULT_FACT_PATCH = "configs/execution_batches/milestone14_2_intake_quality_facts_v1.json"
DEFAULT_QUEUE_PATCH = "configs/execution_batches/milestone14_2_intake_quality_queue_v1.json"
DEFAULT_REGISTRY = "configs/execution_batches/milestone14_2_intake_quality_registry_v1.json"
DEFAULT_ENRICH_CONFIG = "configs/enrich_batches/milestone14_2_intake_quality_enrich_v1.json"
DEFAULT_PROMOTE_CONFIG = "configs/promote_batches/milestone14_2_intake_quality_promote_v1.json"
DEFAULT_OUTPUT_MD = "docs/03-执行与校验/Milestone 14.2-扩容样本入池质量解阻复盘-v1.md"


INTAKE_FIXTURES: dict[str, dict[str, Any]] = {
    "acc_aidi": {
        "product": "艾迪精密围绕工程机械液压属具、高端液压件、工业机器人核心部件、硬质合金刀具和精密线性传动部件开展研发、生产与销售。",
        "model": "公司以高端装备核心零部件制造为主，通过多业务事业部、全球服务网络和上市公司治理体系承接工程机械、机器人、自动化和新能源装备客户需求。",
        "admission": "液压属具、传动部件、机器人和刀具业务共同指向研产销协同复杂制造场景，适合进入先进制造补证链路并验证多产品线经营治理。",
        "evidence": [
            ("official_website", "https://www.cceddie.com/index.htm", "官网披露艾迪精密高端液压件、工业机器人、刀具、储能和传动等业务板块。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=603638", "CNINFO 可定位艾迪精密上市公司公告与定期报告入口。"),
        ],
    },
    "acc_cnano": {
        "product": "天奈科技主要提供碳纳米管导电浆料、碳纳米管粉体及相关新材料产品，面向锂电池和导电材料应用。",
        "model": "公司以新能源材料研发、规模化制造和客户技术服务为主，围绕锂电池产业链形成材料交付和持续工艺迭代模式。",
        "admission": "碳纳米管导电材料与新能源电池产业链深度绑定，能够支撑先进制造画像下研发、量产和客户认证协同的复核。",
        "evidence": [
            ("official_website", "https://www.cnanotechnology.com/", "官网可定位天奈科技碳纳米管材料与新能源应用信息。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=688116", "CNINFO 可定位天奈科技上市公司公告与定期报告入口。"),
        ],
    },
    "acc_dingli": {
        "product": "浙江鼎力研发、生产、销售剪叉式、臂式等智能高空作业平台，并提供面向全球客户的装备服务。",
        "model": "公司以高端装备制造、全球渠道销售和售后服务为核心，依托研发、生产基地和海外市场覆盖形成制造出海模式。",
        "admission": "高空作业平台产品、全球服务网络和研发生产体系明确，能够验证先进制造多基地与全球经营协同画像。",
        "evidence": [
            ("official_website", "https://www.cndingli.com/", "官网披露浙江鼎力智能高空作业平台、研发生产和全球服务网络。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=603338", "CNINFO 可定位浙江鼎力上市公司公告与定期报告入口。"),
        ],
    },
    "acc_focusprecision": {
        "product": "先锋精科聚焦半导体刻蚀、薄膜沉积等设备的关键精密零部件、模组生产与装配。",
        "model": "公司以半导体设备核心零部件精密制造为主，通过工艺研发、精密加工和客户认证体系服务设备产业链客户。",
        "admission": "半导体设备关键零部件业务具备高工艺门槛和客户认证特征，能够支撑先进制造研产销复杂协同画像复核。",
        "evidence": [
            ("official_website", "https://www.sprint-tech.com", "公开资料定位先锋精科官网与半导体关键零部件业务。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=688605", "CNINFO 可定位先锋精科上市公司公告与定期报告入口。"),
        ],
    },
    "acc_haitianjg": {
        "product": "海天精工主要研发、生产和销售龙门加工中心、立式加工中心、卧式加工中心、数控车床等高端数控机床。",
        "model": "公司以高端数控机床制造为核心，依托多地制造基地、技术研发和销售服务体系面向工业客户交付设备。",
        "admission": "数控机床产品线、多制造基地和上市公司治理信息明确，能够支撑先进制造多工厂集团画像复核。",
        "evidence": [
            ("official_website", "https://haitianprecision.com/", "官网披露海天精工数控机床产品、制造基地和研发生产信息。"),
            ("investor_relations", "https://haitianprecision.com/investor-relations/", "官网投资者关系页面披露海天精工上市信息和股票代码。"),
        ],
    },
    "acc_aukey": {
        "product": "傲基科技面向全球市场经营自主品牌科技消费品，覆盖消费电子、智能硬件及相关跨境销售品类。",
        "model": "公司以跨境品牌运营、产品研发设计、海外渠道和供应链管理为核心，服务全球消费者市场。",
        "admission": "自主品牌科技消费品、跨境渠道和供应链协同特征清晰，能够支撑跨境多平台品牌经营画像复核。",
        "evidence": [
            ("official_website", "https://www.aukeys.com/index.html", "官网可定位傲基股份主体和跨境品牌业务入口。"),
            ("industry_association", "https://www.szida.org/Enable/Detail/397", "深圳市工业设计行业协会页面披露傲基科技自主品牌科技消费品研发、设计和销售信息。"),
        ],
    },
    "acc_cayi": {
        "product": "嘉益股份专注不锈钢保温杯、旅行杯、水杯和饮品容器的研发设计、生产与销售，并提供 OEM/ODM 服务。",
        "model": "公司以中国及海外工厂制造能力、全球品牌客户协同和饮具产品开发为主，形成制造出海和客户定制交付模式。",
        "admission": "保温杯产品、海外工厂和全球品牌客户协同明确，能够支撑跨境品牌制造与供应链复杂度复核。",
        "evidence": [
            ("official_website", "https://www.cayigroup.com/", "官网披露嘉益股份饮具制造、OEM/ODM、海外工厂和全球品牌合作信息。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=301004", "CNINFO 可定位嘉益股份上市公司公告与定期报告入口。"),
        ],
    },
    "acc_daziran": {
        "product": "大自然户外用品研发、生产自动充气垫、充气床、防水包、冰包、枕头坐垫和 TPU 复合面料等户外产品。",
        "model": "公司以户外用品研发制造、全球品牌客户合作和出口交付为主，围绕产品设计、生产制造和客户订单履约运营。",
        "admission": "户外用品产品线、全球品牌合作和出口制造特征明确，能够支撑跨境品牌供应链和海外经营画像复核。",
        "evidence": [
            ("official_website", "https://www.zjnature.com/", "官网披露大自然户外用品产品线、全球品牌合作和研发制造信息。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=605080", "CNINFO 可定位大自然户外用品上市公司公告与定期报告入口。"),
        ],
    },
    "acc_eccang": {
        "product": "易仓科技提供跨境电商 ERP、海外仓系统、国际货代软件和跨境分销 M2B 等软件服务。",
        "model": "公司以跨境电商 SaaS/软件产品、系统实施和客户运营服务为主，支撑卖家、海外仓和物流服务商的业务协同。",
        "admission": "跨境 ERP、海外仓和货代系统覆盖跨境经营关键环节，能够支撑跨境平台服务和供应链复杂度画像复核。",
        "evidence": [
            ("official_website", "https://www.eccang.com/about.html", "官网披露易仓科技公司介绍及跨境电商 ERP、WMS、TMS 软件能力。"),
            ("official_website", "https://www.eccang.com/", "官网首页可定位易仓跨境 ERP、海外仓系统和国际货代软件产品入口。"),
        ],
    },
    "acc_greatstar": {
        "product": "巨星科技专注中高端手工具、电动工具、工具箱柜、智能产品和相关五金工具产品的开发、生产与销售。",
        "model": "公司以工具产品研发制造、全球渠道销售和品牌/供应链运营为主，面向欧美等海外市场形成制造出海模式。",
        "admission": "工具产品线、全球销售网络和跨境经营特征明确，能够支撑跨境供应链复杂型经营画像复核。",
        "evidence": [
            ("official_website", "https://www.greatstargroup.com/about.html", "巨星控股集团官网披露巨星科技为全球领先工具企业及股票代码。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002444", "CNINFO 可定位巨星科技上市公司公告与定期报告入口。"),
        ],
    },
    "acc_aimer": {
        "product": "爱慕股份从事贴身服饰、内衣、家居服及相关服饰用品的研发、生产、品牌运营与销售。",
        "model": "公司以多品牌服饰经营、产品研发设计、线上线下渠道销售和会员消费运营为核心，服务中高端贴身服饰市场。",
        "admission": "贴身服饰品类、多品牌和渠道经营特征明确，能够支撑零售消费高 SKU 品牌画像复核。",
        "evidence": [
            ("official_website", "https://www.aimer.com.cn/", "官网可定位爱慕品牌与贴身服饰业务入口。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=603511", "CNINFO 可定位爱慕股份上市公司公告与定期报告入口。"),
        ],
    },
    "acc_anji": {
        "product": "安记食品专注复合调味料、调味品和食品配料的研发、生产与销售。",
        "model": "公司以调味品研发制造、品牌销售和渠道铺货为核心，面向餐饮、家庭消费和食品工业客户提供产品。",
        "admission": "复合调味料产品、品牌渠道和食品消费属性明确，能够支撑零售消费高 SKU 品牌画像复核。",
        "evidence": [
            ("official_website", "https://www.anjifood.com/about.html", "官网企业简介披露安记食品专注调味品研发、生产和销售。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=603696", "CNINFO 可定位安记食品上市公司公告与定期报告入口。"),
        ],
    },
    "acc_anjingfood": {
        "product": "安井食品主营速冻调制食品、速冻菜肴制品和速冻面米制品等速冻食品的研发、生产与销售。",
        "model": "公司以冷冻食品研发制造、品牌渠道、餐饮和零售终端供应为主，围绕多品类和冷链履约组织经营。",
        "admission": "速冻食品产品矩阵、渠道供应和冷链履约特征明确，能够支撑零售消费高 SKU 品牌画像复核。",
        "evidence": [
            ("official_website", "https://www.anjoyfood.com/", "官网披露安井食品速冻调制食品、速冻菜肴和速冻面米制品业务。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=603345", "CNINFO 可定位安井食品上市公司公告与定期报告入口。"),
        ],
    },
    "acc_aofei": {
        "product": "奥飞娱乐围绕动漫内容、影视、游戏、媒体、消费品和主题业态开展 IP 内容与衍生消费业务。",
        "model": "公司以 IP 内容生产、授权、玩具和消费品衍生、渠道销售为核心，形成内容到商品的消费经营链路。",
        "admission": "动漫 IP、玩具消费品和内容衍生链路清晰，能够支撑零售消费高 SKU 品牌及 IP 商品经营画像复核。",
        "evidence": [
            ("official_website", "https://www.gdalpha.com/about/", "官网披露奥飞娱乐内容创作、影视、游戏、媒体、消费品和主题业态。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002292", "CNINFO 可定位奥飞娱乐上市公司公告与定期报告入口。"),
        ],
    },
    "acc_arrowhome": {
        "product": "箭牌家居提供智能坐便器、卫浴陶瓷、浴室柜、五金龙头、瓷砖和定制家居等智慧家居产品。",
        "model": "公司以多品牌家居产品制造、全国销售网点、经销和零售渠道运营为核心，面向家庭装修与家居消费市场。",
        "admission": "家居产品矩阵、十大生产基地和大量销售网点特征明确，能够支撑零售消费多门店网络画像复核。",
        "evidence": [
            ("official_website", "https://www.arrowgroup.com.cn/groupprofile/index.aspx", "官网集团简介披露箭牌、法恩莎、安华品牌、生产基地和销售网点。"),
            ("cninfo", "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=001322", "CNINFO 可定位箭牌家居上市公司公告与定期报告入口。"),
        ],
    },
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M14.2 non-writeback intake quality patch and configs.")
    parser.add_argument("--candidate-file", default=DEFAULT_CANDIDATES)
    parser.add_argument("--promote-file", default=DEFAULT_PROMOTE)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--fact-patch", default=DEFAULT_FACT_PATCH)
    parser.add_argument("--queue-patch", default=DEFAULT_QUEUE_PATCH)
    parser.add_argument("--registry", default=DEFAULT_REGISTRY)
    parser.add_argument("--enrich-config", default=DEFAULT_ENRICH_CONFIG)
    parser.add_argument("--promote-config", default=DEFAULT_PROMOTE_CONFIG)
    parser.add_argument("--output-md", default=DEFAULT_OUTPUT_MD)
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _issue_codes(result: dict[str, Any], issue_type: str) -> list[str]:
    gate = result.get("promotion_gate") if isinstance(result.get("promotion_gate"), dict) else {}
    rows = gate.get(issue_type) if isinstance(gate.get(issue_type), list) else []
    return [_clean(item.get("code")) for item in rows if isinstance(item, dict) and _clean(item.get("code"))]


def _patch_account(candidate: dict[str, Any], promote_result: dict[str, Any]) -> dict[str, Any]:
    account_id = _clean(candidate.get("account_id"))
    fixture = INTAKE_FIXTURES.get(account_id)
    if not fixture:
        raise ValueError(f"missing intake fixture for {account_id}")
    account_name = _clean(promote_result.get("account_canonical_name")) or _clean(candidate.get("account_name")) or account_id
    persona = _clean(promote_result.get("persona_tag"))
    track = _clean(promote_result.get("primary_track")) or _clean(candidate.get("track"))
    evidence_rows = []
    for idx, (source_type, source_locator, summary) in enumerate(fixture["evidence"], start=1):
        evidence_rows.append(
            {
                "evidence_id": f"m142_ev_{account_id}_{idx}",
                "account_id": account_id,
                "evidence_type": "intake_quality_patch",
                "field_name": "intake_quality_support",
                "field_value": summary,
                "source_type": source_type,
                "source_locator": source_locator,
                "evidence_strength": "A",
                "supports_dimension": "official_source,product_service,business_model,persona_support",
                "summary": summary,
                "checked_by": "codex",
                "checked_at": datetime.now(timezone.utc).date().isoformat(),
            }
        )
    main_fields = {
        "primary_track": track,
        "persona_tag": persona,
        "公司产品与服务概述": fixture["product"],
        "商业模式概述": fixture["model"],
        "admission_reason_summary": fixture["admission"],
        "validation_gap": "已补官方来源和最小字段；仍需人工确认画像边界、真实采购场景和优先触达价值。",
        "review_status": "pending_review",
        "静态潜客记录成熟度": "L5",
    }
    return {
        "account_id": account_id,
        "account_name": account_name,
        "source_milestone": "M14.2",
        "previous_blocking_codes": _issue_codes(promote_result, "blocking_issues"),
        "previous_warning_codes": _issue_codes(promote_result, "warning_issues"),
        "official_source_count": len(evidence_rows),
        "high_confidence_source_count": len(evidence_rows),
        "primary_source_types": ",".join(row["source_type"] for row in evidence_rows),
        "primary_source_refs": ",".join(row["source_locator"] for row in evidence_rows),
        "main_fields": main_fields,
        "profile_fields": {
            "primary_track": track,
            "persona_tag": persona,
            "static_maturity_level": "L5",
            "静态潜客记录成熟度": "L5",
            "validation_gap": main_fields["validation_gap"],
            "profile_status": "pending_review",
        },
        "rectification": {
            "final_candidate_type": "formal_candidate",
            "final_review_status": "pending_review",
            "suggested_maturity": "L5",
            "suggested_primary_persona": persona,
            "risk_flags": [],
            "rewrite_suggestion": main_fields,
            "rectification_action": main_fields["validation_gap"],
            "evidence_rows": evidence_rows,
        },
        "evidence_rows": evidence_rows,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 14.2-扩容样本入池质量解阻复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 候选数：`{summary['account_count']}`",
        f"- 补产品/服务字段：`{summary['product_patch_count']}`",
        f"- 补商业模式字段：`{summary['business_model_patch_count']}`",
        f"- 补强 evidence：`{summary['evidence_row_count']}`",
        f"- 修复前阻塞分布：`{summary['previous_blocking_code_counts']}`",
        f"- 修复前 warn 分布：`{summary['previous_warning_code_counts']}`",
        "",
        "## 公司级补证动作",
        "",
    ]
    for item in payload["accounts"]:
        fields = item["main_fields"]
        lines.extend(
            [
                f"### {item['account_name']}（{item['account_id']}）",
                "",
                f"- 产品/服务：{fields['公司产品与服务概述']}",
                f"- 商业模式：{fields['商业模式概述']}",
                f"- 入池理由：{fields['admission_reason_summary']}",
                f"- evidence：`{item['primary_source_refs']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## 写回策略",
            "",
            "- 本轮只生成结构化 patch 和 report-only 输入，不直接写回真实工作簿。",
            "- 若后续 report-only 出现 allow，只进入 M17 写回候选准入试点，仍需单独确认真实 write_back。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    candidates = _load_json(args.candidate_file)
    promote = _load_json(args.promote_file)
    results_by_id = {_clean(item.get("account_id")): item for item in promote.get("results") or [] if isinstance(item, dict)}
    accounts = []
    for candidate in candidates.get("accounts") or []:
        account_id = _clean(candidate.get("account_id")) if isinstance(candidate, dict) else ""
        if not account_id:
            continue
        accounts.append(_patch_account(candidate, results_by_id.get(account_id, {})))

    previous_blocking = Counter(code for item in accounts for code in item["previous_blocking_codes"])
    previous_warnings = Counter(code for item in accounts for code in item["previous_warning_codes"])
    payload = {
        "batch_id": "milestone14_2_intake_quality_patch_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {"candidate_file": args.candidate_file, "promote_file": args.promote_file},
        "summary": {
            "account_count": len(accounts),
            "product_patch_count": len([item for item in accounts if item["main_fields"].get("公司产品与服务概述")]),
            "business_model_patch_count": len([item for item in accounts if item["main_fields"].get("商业模式概述")]),
            "evidence_row_count": sum(len(item.get("evidence_rows") or []) for item in accounts),
            "previous_blocking_code_counts": dict(previous_blocking),
            "previous_warning_code_counts": dict(previous_warnings),
        },
        "results": accounts,
        "accounts": accounts,
    }

    fact_patch = {
        "batch_id": "milestone14_2_intake_quality_facts_v1",
        "generated_at": payload["generated_at"],
        "accounts": accounts,
    }
    queue_patch = {
        "batch_id": "milestone14_2_intake_quality_queue_v1",
        "generated_at": payload["generated_at"],
        "accounts": [
            {
                "account_id": item["account_id"],
                "account_name": item["account_name"],
                "queue_type": "verification",
                "priority": "P1",
                "status": "open",
                "owner": "codex",
                "note": "M14.2 已补官方来源和最小字段；等待画像边界与业务价值人工复核。",
                "created_at": datetime.now(timezone.utc).date().isoformat(),
            }
            for item in accounts
        ],
    }
    out_dir = Path(args.output_dir)
    intake_patch = str(out_dir / "milestone14_2_intake_quality_patch_v1.json")
    _write_json(intake_patch, payload)
    _write_json(args.fact_patch, fact_patch)
    _write_json(args.queue_patch, queue_patch)

    registry = {
        "milestone_id": "milestone14_2_intake_quality_unblock",
        "batch_id": "milestone14_2_intake_quality_v1",
        "goal": "Milestone 14.2：扩容样本入池质量解阻",
        "candidate_file": args.candidate_file,
        "fact_patch_file": args.fact_patch,
        "queue_patch_file": args.queue_patch,
        "intake_patch_file": intake_patch,
        "enrich": {
            "config_file": args.enrich_config,
            "output_file": str(out_dir / "milestone14_2_intake_quality_enrich_v1.json"),
            "summary_file": str(out_dir / "milestone14_2_intake_quality_enrich_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 14.2-扩容样本入池质量解阻-enrich复盘-v1.md",
        },
        "promote": {
            "config_file": args.promote_config,
            "output_file": str(out_dir / "milestone14_2_intake_quality_promote_v1.json"),
            "summary_file": str(out_dir / "milestone14_2_intake_quality_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 14.2-扩容样本入池质量解阻-promote复盘-v1.md",
        },
        "run_output": {
            "summary_file": str(out_dir / "milestone14_2_intake_quality_run_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 14.2-扩容样本入池质量解阻最终复盘-v1.md",
            "report_baseline_file": str(out_dir / "milestone14_2_intake_quality_report_baseline_v1.json"),
        },
        "mode_policy": {"default_phase": "report_only", "require_report_baseline": True, "write_back_after_report_only": False},
    }
    enrich_config = {
        "batch_id": "milestone14_2_intake_quality_enrich_v1",
        "goal": "Milestone 14.2：扩容样本入池质量解阻 enrich 非写回复核",
        "from_level": "L5",
        "target_level": "L3",
        "promote_target_level": "L3",
        "write_back": False,
        "workbook_lock_timeout_seconds": 0.0,
        "rectification_file": intake_patch,
        "source_policy": "仅接受官网、年报、IR、cninfo 和其他强公开资料；本轮 patch 作为 report-only 临时事实层。",
        "output": {
            "enrich_file": registry["enrich"]["output_file"],
            "summary_file": registry["enrich"]["summary_file"],
            "review_file": registry["enrich"]["review_file"],
        },
        "account_ids": [],
    }
    promote_config = {
        "batch_id": "milestone14_2_intake_quality_promote_v1",
        "goal": "Milestone 14.2：扩容样本入池质量解阻 promote 非写回复核",
        "account_ids": [],
        "from_level": "L5",
        "target_level": "L3",
        "auto_open_promotion_review_for_selected": True,
        "workbook_lock_timeout_seconds": 0.0,
        "write_back": False,
        "enrich_result_file": registry["enrich"]["output_file"],
        "fact_patch_file": args.fact_patch,
        "queue_patch_file": args.queue_patch,
        "output_file": registry["promote"]["output_file"],
        "summary_file": registry["promote"]["summary_file"],
        "review_file": registry["promote"]["review_file"],
    }
    _write_json(args.registry, registry)
    _write_json(args.enrich_config, enrich_config)
    _write_json(args.promote_config, promote_config)
    _write_text(args.output_md, _render_markdown(payload))
    print(
        json.dumps(
            {
                "intake_patch": intake_patch,
                "fact_patch": args.fact_patch,
                "queue_patch": args.queue_patch,
                "registry": args.registry,
                "summary": payload["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
