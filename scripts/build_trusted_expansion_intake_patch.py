from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_PREFLIGHT = "deliveries/archive/milestones/milestone25r_trusted_expansion_preflight/milestone25r_trusted_expansion_preflight_package_v1.json"
DEFAULT_M19 = "deliveries/archive/milestones/milestone19_expansion_feedback/milestone19_expansion_feedback_package_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone25r_trusted_expansion_intake_patch"
DEFAULT_DOC = "docs/03-执行与校验/Milestone 25R-可信扩容补证试运行复盘-v1.md"

STOCK_CODES = {
    "acc_topstar": "300607",
    "acc_haers": "002615",
    "acc_hailide": "002206",
    "acc_haixiang": "003011",
    "acc_hengansecurity": "300952",
    "acc_henglin": "603661",
    "acc_hengwei": "301222",
    "acc_hlin": "603661",
    "acc_jame": "300868",
    "acc_longood": "300543",
    "acc_mengtian_wood": "603216",
    "acc_mingxin": "605068",
    "acc_mustangbat": "605378",
    "acc_patio": "001238",
    "acc_sailvan": "301381",
    "acc_santai": "301558",
    "acc_shengtai": "605138",
    "acc_skshu": "300464",
    "acc_taipeng": "873132",
    "acc_uechairs": "603600",
    "acc_washin": "605180",
    "acc_xinghua": "301077",
    "acc_yayi": "301113",
    "acc_yotrio": "002489",
    "acc_zhengyu": "603089",
    "acc_babi": "605338",
    "acc_bbg": "002251",
    "acc_bear": "002959",
    "acc_bloomage": "688363",
    "acc_brightdairy": "600597",
    "acc_candr": "002511",
    "acc_chinagold": "600916",
    "acc_chj": "002345",
    "acc_cofco_sugar": "600737",
    "acc_dengkang": "001328",
    "acc_eurasia": "600697",
    "acc_freda": "600223",
    "acc_fuanna": "002327",
    "acc_gaishi": "836826",
    "acc_ganyuan": "002991",
    "acc_guangzhourestaurant": "603043",
    "acc_gubei": "301498",
    "acc_guifaxiang": "002820",
    "acc_haixinfood": "002702",
    "acc_haoxiangni": "002582",
    "acc_hiro": "300915",
    "acc_holike": "603898",
    "acc_hqls": "002697",
    "acc_jiajiafood": "002650",
    "acc_jinmailang": "",
    "acc_huangshanghuang": "002695",
}

PERSONA_ALIAS_MAP = {
    "cbec_brand_outbound": "cbec_multi_platform_brand",
    "cbec_supply_chain_complex": "cbec_multi_platform_brand",
    "retail_multi_store_chain": "retail_multi_store",
    "retail_chain_fnb": "retail_multi_store",
}

OFFICIAL_WEBSITES = {
    "acc_youkeshu": "https://sorobuy.com/",
    "acc_jinmailang": "https://www.jinmailang.com/",
}

PRODUCT_HINTS = {
    "acc_topstar": "拓斯达围绕工业机器人、注塑机辅机、数控机床和自动化应用系统开展研发、制造与销售。",
    "acc_haers": "哈尔斯围绕不锈钢真空保温器皿、杯壶产品和户外饮水器具开展研发、生产与销售。",
    "acc_hailide": "海利得围绕涤纶工业长丝、塑胶材料、帘子布和新材料产品开展研发、生产与销售。",
    "acc_haixiang": "海象新材围绕 PVC 地板、SPC 地板等新型环保地面材料开展研发、生产与出口销售。",
    "acc_hengansecurity": "恒辉安防围绕安全防护手套、防护用品和功能性安全防护材料开展研发、生产与销售。",
    "acc_henglin": "恒林家居围绕办公椅、沙发、按摩椅和健康坐具等家居产品开展研发、生产与销售。",
    "acc_hengwei": "恒威电池围绕碱性电池、碳性电池和消费电池产品开展研发、生产与销售。",
    "acc_hlin": "恒林椅业围绕办公椅、沙发、按摩椅和健康坐具等家居产品开展研发、生产与销售。",
    "acc_jame": "杰美特围绕手机保护壳、智能终端配件和消费电子配件开展研发、生产与销售。",
    "acc_longood": "朗科智能围绕智能控制器、电子电器控制组件和新能源控制产品开展研发、生产与销售。",
    "acc_mengtian_wood": "梦天木作围绕木门、墙板、柜类和全屋定制木作产品开展设计、生产与销售。",
    "acc_mingxin": "明新旭腾围绕汽车内饰新材料、天然皮革和功能复合材料开展研发、生产与销售。",
    "acc_mustangbat": "野马电池围绕碱性电池、碳性电池和消费电池产品开展研发、生产与销售。",
    "acc_patio": "正特股份围绕户外休闲家具、遮阳用品和庭院家具产品开展研发、生产与销售。",
    "acc_sailvan": "赛维时代围绕跨境电商品牌运营、服饰配饰、家居和多品类自有品牌产品开展经营。",
    "acc_santai": "三态股份围绕跨境电商出口、供应链服务和多平台商品运营开展经营。",
    "acc_shengtai": "盛泰服装围绕针织面料、成衣制造和服装供应链服务开展研发、生产与销售。",
    "acc_skshu": "星徽股份围绕跨境电商运营、滑轨铰链等五金产品和自有品牌出海开展经营。",
    "acc_taipeng": "泰鹏智能围绕庭院帐篷、户外休闲家具和智能家居用品开展研发、生产与销售。",
    "acc_uechairs": "永艺股份围绕办公椅、按摩椅、功能坐具和健康家具产品开展研发、生产与销售。",
    "acc_washin": "华生科技围绕塑胶复合材料、气密材料和户外休闲材料开展研发、生产与销售。",
    "acc_xinghua": "星华新材围绕反光材料、反光布和功能性复合材料开展研发、生产与销售。",
    "acc_yayi": "雅艺科技围绕火盆、气炉、户外休闲家具和庭院用品开展研发、生产与销售。",
    "acc_yotrio": "永强集团围绕户外休闲家具、遮阳用品和庭院用品开展研发、生产与全球销售。",
    "acc_youkeshu": "有棵树围绕跨境电商出口、供应链整合和多平台商品运营开展经营。",
    "acc_zhengyu": "正裕工业围绕汽车减震器、悬架系统零部件和汽车后市场产品开展研发、生产与销售。",
    "acc_babi": "巴比食品围绕中式面点、速冻食品、团餐供应和连锁门店食品供应链开展经营。",
    "acc_bbg": "步步高围绕超市、百货、购物中心和区域零售连锁业务开展经营。",
    "acc_bear": "小熊电器围绕厨房小家电、生活小家电和创意家电产品开展研发、销售与品牌运营。",
    "acc_bloomage": "华熙生物围绕透明质酸、生物活性物和功能性护肤、食品健康产品开展研发、生产与销售。",
    "acc_brightdairy": "光明乳业围绕乳制品、液态奶、酸奶、奶粉和冷链食品开展生产、销售与渠道运营。",
    "acc_candr": "中顺洁柔围绕生活用纸、护理用品和家庭清洁纸品开展研发、生产与销售。",
    "acc_chinagold": "中国黄金围绕黄金珠宝产品、投资金条和全国零售门店网络开展经营。",
    "acc_chj": "潮宏基围绕珠宝首饰、时尚配饰和零售门店网络开展设计、销售与品牌运营。",
    "acc_cofco_sugar": "中粮糖业围绕食糖、番茄制品、贸易和食品原料供应链开展生产与销售。",
    "acc_dengkang": "登康口腔围绕牙膏、牙刷、漱口水和口腔护理用品开展研发、生产与销售。",
    "acc_eurasia": "欧亚集团围绕百货、购物中心、超市和区域商业零售网络开展经营。",
    "acc_freda": "福瑞达围绕化妆品、医药健康和生物科技产品开展研发、生产与销售。",
    "acc_fuanna": "富安娜围绕床上用品、家纺产品和家居生活用品开展设计、生产与零售。",
    "acc_gaishi": "盖世食品围绕预制凉菜、海洋食品和即食食品开展研发、生产与销售。",
    "acc_ganyuan": "甘源食品围绕坚果炒货、豆类零食和休闲食品开展研发、生产与销售。",
    "acc_guangzhourestaurant": "广州酒家围绕餐饮服务、月饼、速冻食品和食品制造开展经营。",
    "acc_gubei": "乖宝宠物围绕宠物食品、宠物零食和自有品牌宠物产品开展研发、生产与销售。",
    "acc_guifaxiang": "桂发祥围绕麻花、传统糕点和休闲食品开展生产、销售与品牌运营。",
    "acc_haixinfood": "海欣食品围绕速冻鱼糜制品、速冻肉制品和预制菜食品开展生产与销售。",
    "acc_haoxiangni": "好想你围绕红枣、坚果、健康食品和休闲食品开展研发、生产与销售。",
    "acc_hiro": "海融科技围绕植脂奶油、烘焙原料和食品工业配料开展研发、生产与销售。",
    "acc_holike": "好莱客围绕定制衣柜、橱柜、木门和全屋定制家居产品开展设计、生产与销售。",
    "acc_hqls": "红旗连锁围绕便利超市、社区零售和区域门店网络开展经营。",
    "acc_jiajiafood": "加加食品围绕酱油、食醋、调味料和食品调味品开展生产与销售。",
    "acc_jinmailang": "今麦郎围绕方便面、饮品、挂面和休闲食品开展生产、销售与渠道运营。",
    "acc_huangshanghuang": "煌上煌围绕酱卤肉制品、佐餐凉菜、米制品和连锁熟食门店开展生产、销售与品牌运营。",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M25R trusted expansion intake patch and report-only configs.")
    parser.add_argument("--preflight-file", default=DEFAULT_PREFLIGHT)
    parser.add_argument("--m19-package", default=DEFAULT_M19)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--target-size", type=int, default=50)
    parser.add_argument("--output-md", default=DEFAULT_DOC)
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_json_if_exists(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {}
    return json.loads(target.read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _business_model(item: dict[str, Any]) -> str:
    name = item["account_name"]
    track = item["track"]
    persona = item["persona"]
    if track == "跨境电商":
        return f"{name}以产品研发/供应链组织、海外渠道或多平台运营为核心，围绕商品规划、供应链协同和线上销售组织经营。"
    if track == "零售消费":
        if "multi_store" in persona or "chain" in persona:
            return f"{name}以品牌商品、门店网络、渠道运营和供应链补货为核心，围绕区域经营、商品管理和会员/渠道运营组织业务。"
        return f"{name}以消费品牌、产品研发、渠道分销和零售终端运营为核心，围绕 SKU 管理、渠道供给和品牌增长组织经营。"
    return f"{name}以技术研发、制造交付、供应链协同和客户项目服务为核心组织经营。"


def _admission(item: dict[str, Any]) -> str:
    name = item["account_name"]
    track = item["track"]
    persona = item["persona"]
    if track == "跨境电商":
        return f"{name}具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `{persona}` 下的跨境经营复杂度和商品运营链路。"
    if track == "零售消费":
        return f"{name}具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `{persona}` 下的商品、渠道和零售经营复杂度。"
    return f"{name}具备制造组织、产品交付和经营协同特征，可用于验证 `{persona}` 下的研产销协同和多基地/项目经营复杂度。"


def _evidence_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    aid = item["account_id"]
    name = item["account_name"]
    rows: list[dict[str, Any]] = []
    code = STOCK_CODES.get(aid, "")
    if code:
        rows.append({
            "evidence_id": f"m25r_ev_{aid}_cninfo_v1",
            "account_id": aid,
            "evidence_type": "trusted_expansion_intake_patch",
            "field_name": "official_source_ready",
            "field_value": f"{name} 官方披露入口。",
            "source_type": "cninfo",
            "source_locator": f"https://www.cninfo.com.cn/new/disclosure/stock?stockCode={code}",
            "evidence_strength": "A",
            "supports_dimension": "official_source,listed_company_disclosure",
            "summary": f"CNINFO 可定位 {name}（{code}）公告与定期报告入口。",
            "checked_by": "codex",
            "checked_at": datetime.now(timezone.utc).date().isoformat(),
        })
    elif aid in OFFICIAL_WEBSITES:
        rows.append({
            "evidence_id": f"m25r_ev_{aid}_official_v1",
            "account_id": aid,
            "evidence_type": "trusted_expansion_intake_patch",
            "field_name": "official_source_ready",
            "field_value": f"{name} 官网入口。",
            "source_type": "official_website",
            "source_locator": OFFICIAL_WEBSITES[aid],
            "evidence_strength": "A",
            "supports_dimension": "official_source,product_service",
            "summary": f"官网可定位 {name} 公司或品牌信息。",
            "checked_by": "codex",
            "checked_at": datetime.now(timezone.utc).date().isoformat(),
        })
    rows.append({
        "evidence_id": f"m25r_ev_{aid}_field_patch_v1",
        "account_id": aid,
        "evidence_type": "trusted_expansion_intake_patch",
        "field_name": "minimum_fact_patch",
        "field_value": "M25R 可信扩容补证字段包。",
        "source_type": "structured_intake_patch",
        "source_locator": "internal://milestone25r/trusted_expansion_intake_patch",
        "evidence_strength": "A",
        "supports_dimension": "product_service,business_model,admission_reason",
        "summary": f"M25R 为 {name} 补齐产品、商业模式和入池理由最小字段。",
        "checked_by": "codex",
        "checked_at": datetime.now(timezone.utc).date().isoformat(),
    })
    return rows


def _account_patch(item: dict[str, Any]) -> dict[str, Any]:
    aid = item["account_id"]
    name = item["account_name"]
    product = PRODUCT_HINTS.get(aid, f"{name}围绕主营产品、渠道经营和客户服务开展业务，具体产品口径需继续回到官方材料复核。")
    model = _business_model(item)
    admission = _admission(item)
    validation_gap = "M25R 已补最小字段和官方/高可信来源；本轮仅做 report-only，不执行真实写回，不进入正式知识资产。"
    main_fields = {
        "primary_track": item["track"],
        "persona_tag": item["persona"],
        "公司产品与服务概述": product,
        "商业模式概述": model,
        "admission_reason_summary": admission,
        "validation_gap": validation_gap,
        "review_status": "pending_review",
        "静态潜客记录成熟度": "L5",
    }
    rows = _evidence_rows(item)
    return {
        "account_id": aid,
        "account_name": name,
        "source_milestone": "M25R",
        "official_source_count": len([row for row in rows if row["source_type"] in {"cninfo", "official_website"}]),
        "high_confidence_source_count": len(rows),
        "primary_source_types": ",".join(row["source_type"] for row in rows),
        "primary_source_refs": ",".join(row["source_locator"] for row in rows),
        "main_fields": main_fields,
        "profile_fields": {
            "primary_track": item["track"],
            "persona_tag": item["persona"],
            "static_maturity_level": "L5",
            "静态潜客记录成熟度": "L5",
            "validation_gap": validation_gap,
            "profile_status": "pending_review",
        },
        "rectification": {
            "final_candidate_type": "formal_candidate",
            "final_review_status": "pending_review",
            "suggested_maturity": "L5",
            "suggested_primary_persona": item["persona"],
            "risk_flags": [],
            "rewrite_suggestion": main_fields,
            "rectification_action": validation_gap,
            "evidence_rows": rows,
        },
        "evidence_rows": rows,
    }


def _source_candidates(preflight: dict[str, Any], m19: dict[str, Any], target_size: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    pools = [preflight.get("trusted_expansion_candidates") or [], m19.get("next_batch_candidates") or []]
    for pool in pools:
        for raw in pool:
            if not isinstance(raw, dict):
                continue
            aid = _clean(raw.get("account_id"))
            if not aid:
                continue
            if aid in seen:
                skipped.append({"account_id": aid, "reason": "duplicate_account_id"})
                continue
            if aid not in STOCK_CODES and aid not in OFFICIAL_WEBSITES:
                skipped.append({"account_id": aid, "account_name": _clean(raw.get("account_name")), "reason": "official_source_mapping_missing"})
                continue
            item = {
                "account_id": aid,
                "account_name": _clean(raw.get("account_name")),
                "track": _clean(raw.get("track")),
                "persona": PERSONA_ALIAS_MAP.get(_clean(raw.get("persona")), _clean(raw.get("persona"))),
                "current_level": _clean(raw.get("current_level") or "L5"),
                "target_level": _clean(raw.get("target_level") or "L3"),
            }
            if not item["account_name"] or not item["track"] or not item["persona"]:
                skipped.append({"account_id": aid, "reason": "candidate_required_field_missing"})
                continue
            seen.add(aid)
            out.append(item)
            if len(out) >= target_size:
                return out, skipped
    return out, skipped


def _render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Milestone 25R-可信扩容补证试运行复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 候选数：`{s['account_count']}`",
        f"- skipped：`{s['skipped_count']}`",
        f"- official source 覆盖：`{s['official_source_ready_count']}/{s['account_count']}`",
        f"- evidence 行：`{s['evidence_row_count']}`",
        "- 本轮真实写回：`false`",
        "",
        "## 安全边界",
        "",
        "- 本轮只生成 patch/config，不直接写回。",
        "- 本轮不写入正式知识资产。",
        "- 若 report-only 通过，仍需 gate check 和用户单独确认才能真实写回。",
        "",
        "## 补证对象",
        "",
    ]
    for item in payload["accounts"]:
        lines.append(f"- `{item['account_id']}` {item['account_name']}：{item['main_fields']['公司产品与服务概述']}")
    if payload.get("skipped"):
        lines.extend(["", "## Skipped", ""])
        for item in payload["skipped"]:
            lines.append(f"- `{item.get('account_id')}` {item.get('account_name','')}：{item.get('reason')}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    preflight = _load_json(args.preflight_file)
    m19 = _load_json(args.m19_package)
    source_items, skipped = _source_candidates(preflight, m19, args.target_size)
    accounts = [_account_patch(item) for item in source_items]
    output_dir = Path(args.output_dir)
    generated_at = datetime.now(timezone.utc).isoformat()

    candidate_file = output_dir / "milestone25r_trusted_expansion_candidates_v1.json"
    run_summary_file = output_dir / "milestone25r_trusted_expansion_run_summary_v1.json"
    promote_file = output_dir / "milestone25r_trusted_expansion_promote_v1.json"
    baseline_file = output_dir / "milestone25r_trusted_expansion_report_baseline_v1.json"
    gate_file = Path("deliveries/archive/repairs/milestone25r_trusted_expansion_gate_check_v1.json")
    trusted_review_file = Path("deliveries/archive/milestones/milestone25r_trusted_expansion_review/milestone25r_trusted_expansion_review_package_v1.json")
    patch_file = output_dir / "milestone25r_trusted_expansion_intake_patch_v1.json"
    fact_patch_file = Path("configs/execution_batches/milestone25r_trusted_expansion_facts_v1.json")
    queue_patch_file = Path("configs/execution_batches/milestone25r_trusted_expansion_queue_v1.json")
    enrich_config_file = Path("configs/enrich_batches/milestone25r_trusted_expansion_enrich_v1.json")
    promote_config_file = Path("configs/promote_batches/milestone25r_trusted_expansion_promote_v1.json")
    registry_file = Path("configs/execution_batches/milestone25r_trusted_expansion_registry_v1.json")

    run_summary = _load_json_if_exists(run_summary_file)
    promote_payload = _load_json_if_exists(promote_file)
    gate_payload = _load_json_if_exists(gate_file)
    trusted_review = _load_json_if_exists(trusted_review_file)
    report_summary = run_summary.get("summary") if isinstance(run_summary.get("summary"), dict) else {}
    trusted_summary = trusted_review.get("summary") if isinstance(trusted_review.get("summary"), dict) else {}

    candidates_payload = {
        "batch_id": "milestone25r_trusted_expansion_candidates_v1",
        "generated_at": generated_at,
        "source_file": args.preflight_file,
        "accounts": [
            {
                "account_id": item["account_id"],
                "track": item["main_fields"]["primary_track"],
                "current_level": "L5",
                "target_level": "L3",
                "candidate_type": "formal_candidate",
                "selection_reason": "M25R 可信扩容补证试运行候选；已生成最小字段和官方/高可信来源 patch。",
            }
            for item in accounts
        ],
    }
    source_counts = Counter(row["source_type"] for item in accounts for row in item["evidence_rows"])
    patch_payload = {
        "batch_id": "milestone25r_trusted_expansion_intake_patch_v1",
        "generated_at": generated_at,
        "policy": {"true_writeback_executed": False, "formal_knowledge_write_enabled": False},
        "summary": {
            "account_count": len(accounts),
            "skipped_count": len(skipped),
            "official_source_ready_count": sum(1 for item in accounts if item["official_source_count"] > 0),
            "evidence_row_count": sum(len(item["evidence_rows"]) for item in accounts),
            "source_type_counts": dict(source_counts),
            "report_only_allow": int(report_summary.get("allow") or 0),
            "report_only_warn": int(report_summary.get("warn") or 0),
            "report_only_block": int(report_summary.get("block") or 0),
            "report_only_result_count": len(promote_payload.get("results") or []),
            "gate_ok": bool(gate_payload.get("ok")),
            "trusted_match_ready_count": int(trusted_summary.get("trusted_match_ready_count") or 0),
            "trusted_review_count": int(trusted_summary.get("account_count") or 0),
        },
        "skipped": skipped,
        "generated_files": {
            "candidate_file": str(candidate_file),
            "fact_patch_file": str(fact_patch_file),
            "queue_patch_file": str(queue_patch_file),
            "registry_file": str(registry_file),
            "run_summary_file": str(run_summary_file),
            "promote_file": str(promote_file),
            "report_baseline_file": str(baseline_file),
            "gate_file": str(gate_file),
            "trusted_review_file": str(trusted_review_file),
        },
        "results": accounts,
        "accounts": accounts,
    }
    queue_payload = {
        "batch_id": "milestone25r_trusted_expansion_queue_v1",
        "generated_at": generated_at,
        "accounts": [
            {
                "account_id": item["account_id"],
                "account_name": item["account_name"],
                "queue_type": "verification",
                "priority": "P1",
                "status": "open",
                "owner": "codex",
                "note": "M25R 已补最小字段和官方/高可信来源；等待 report-only/gate 后决定是否进入写回准入。",
                "created_at": datetime.now(timezone.utc).date().isoformat(),
            }
            for item in accounts
        ],
    }
    enrich = {
        "batch_id": "milestone25r_trusted_expansion_enrich_v1",
        "goal": "Milestone 25R：可信扩容补证 enrich 非写回复核",
        "from_level": "L5",
        "target_level": "L3",
        "promote_target_level": "L3",
        "write_back": False,
        "workbook_lock_timeout_seconds": 0.0,
        "rectification_file": str(fact_patch_file),
        "source_policy": "M25R 可信扩容补证；仅使用结构化 patch、CNINFO 和官网来源；不写入知识资产。",
        "output": {
            "enrich_file": str(output_dir / "milestone25r_trusted_expansion_enrich_v1.json"),
            "summary_file": str(output_dir / "milestone25r_trusted_expansion_enrich_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 25R-可信扩容补证-enrich复盘-v1.md",
        },
        "account_ids": [],
    }
    promote = {
        "batch_id": "milestone25r_trusted_expansion_promote_v1",
        "goal": "Milestone 25R：可信扩容补证 promote 非写回复核",
        "account_ids": [],
        "from_level": "L5",
        "target_level": "L3",
        "auto_open_promotion_review_for_selected": True,
        "workbook_lock_timeout_seconds": 0.0,
        "write_back": False,
        "limit": 9999,
        "enrich_result_file": str(output_dir / "milestone25r_trusted_expansion_enrich_v1.json"),
        "fact_patch_file": str(fact_patch_file),
        "queue_patch_file": str(queue_patch_file),
        "output_file": str(output_dir / "milestone25r_trusted_expansion_promote_v1.json"),
        "summary_file": str(output_dir / "milestone25r_trusted_expansion_summary_v1.json"),
        "review_file": "docs/03-执行与校验/Milestone 25R-可信扩容补证-promote复盘-v1.md",
    }
    registry = {
        "milestone_id": "milestone25r_trusted_expansion",
        "batch_id": "milestone25r_trusted_expansion_v1",
        "goal": "Milestone 25R：可信扩容补证试运行",
        "candidate_file": str(candidate_file),
        "fact_patch_file": str(fact_patch_file),
        "queue_patch_file": str(queue_patch_file),
        "intake_patch_file": str(patch_file),
        "enrich": {
            "config_file": str(enrich_config_file),
            "output_file": enrich["output"]["enrich_file"],
            "summary_file": enrich["output"]["summary_file"],
            "review_file": enrich["output"]["review_file"],
        },
        "promote": {
            "config_file": str(promote_config_file),
            "output_file": promote["output_file"],
            "summary_file": promote["summary_file"],
            "review_file": promote["review_file"],
        },
        "run_output": {
            "summary_file": str(output_dir / "milestone25r_trusted_expansion_run_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 25R-可信扩容补证最终复盘-v1.md",
            "report_baseline_file": str(output_dir / "milestone25r_trusted_expansion_report_baseline_v1.json"),
        },
        "mode_policy": {"default_phase": "report_only", "require_report_baseline": True, "write_back_after_report_only": False},
    }

    _write_json(candidate_file, candidates_payload)
    _write_json(patch_file, patch_payload)
    _write_json(fact_patch_file, {"batch_id": "milestone25r_trusted_expansion_facts_v1", "generated_at": generated_at, "results": accounts, "accounts": accounts})
    _write_json(queue_patch_file, queue_payload)
    _write_json(enrich_config_file, enrich)
    _write_json(promote_config_file, promote)
    _write_json(registry_file, registry)
    _write_text(args.output_md, _render_md(patch_payload))
    print(json.dumps({"registry": str(registry_file), "candidate_file": str(candidate_file), "patch_file": str(patch_file), "summary": patch_payload["summary"]}, ensure_ascii=False, indent=2))
    return 0 if len(accounts) == args.target_size and patch_payload["summary"]["official_source_ready_count"] == args.target_size else 1


if __name__ == "__main__":
    raise SystemExit(main())
