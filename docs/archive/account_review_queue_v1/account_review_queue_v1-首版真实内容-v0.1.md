# `account_review_queue_v1` 首版真实内容 v0.1

## 1. 文档目的

本文件把“接下来该补什么、查什么、迁什么”从口头建议转换为结构化工作队列。

当前首版队列主要覆盖三类工作：

1. 已迁入高质量层账户的补证据与边界复核
2. 当前 `L4=14` 的上移 / 迁移准备
3. 大规模迁移 `L5=281` 前的知识抽取和清池准备

## 2. 当前首版队列

| queue_item_id | queue_type | account_id | related_track_id | related_persona_id | priority | status | owner | reason_summary | expected_action | source_context | created_at | resolved_at | resolution_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `q_verify_miniso_structure` | `verification` | `acc_miniso` | `retail_consumer` | `retail_multi_store` | `高` | `open` | `codex_llm` | 名创优品已在 `L1`，但中国经营主体与国内组织结构仍有明显补证据空间。 | 补充中国主体、直营网/加盟或区域经营颗粒度证据。 | `external_target_account_pool_v2-首版真实内容-v0.1.md` | `2026-03-28` |  |  |
| `q_verify_anker_platforms` | `verification` | `acc_anker` | `cross_border_ecommerce` | `cbec_multi_platform_brand` | `高` | `open` | `codex_llm` | 安克已是跨境 `L1`，但平台矩阵与区域经营颗粒度仍偏摘要化。 | 补充多平台、多区域经营强证据。 | `account_evidence_log_v1-首版真实内容-v0.1.md` | `2026-03-28` |  |  |
| `q_verify_luxshare_sites` | `verification` | `acc_luxshare` | `advanced_manufacturing` | `mfg_multi_factory_group` | `高` | `open` | `codex_llm` | 立讯精密作为 `L1` 母样本，仍缺工厂/事业部颗粒度证据。 | 补充多基地、事业部或价值流层证据。 | `account_evidence_log_v1-首版真实内容-v0.1.md` | `2026-03-28` |  |  |
| `q_verify_bestore_inventory` | `verification` | `acc_bestore` | `retail_consumer` | `retail_high_sku_brand` | `中` | `open` | `codex_llm` | 良品铺子已升至 `L2`，但渠道与库存协同证据仍不足。 | 补充 SKU、渠道和库存联动强证据。 | `L4 中可信候选首轮强核验` | `2026-03-28` |  |  |
| `q_verify_songmics_warehouse` | `verification` | `acc_songmics` | `cross_border_ecommerce` | `cbec_multi_platform_brand` | `中` | `open` | `codex_llm` | 致欧家居已升至 `L2`，但海外仓和平台颗粒度仍待补。 | 补充海外仓、平台矩阵或区域经营证据。 | `第二批扩展候选池-v0.3-第二轮核验版` | `2026-03-28` |  |  |
| `q_verify_hla_franchise` | `verification` | `acc_hla` | `retail_consumer` | `retail_multi_store` | `中` | `open` | `codex_llm` | 海澜之家当前为 `L3`，直营网 / 加盟结构与区域经营证据仍有缺口。 | 补充直营网、加盟、门店网络分布证据。 | `L4 中可信候选首轮强核验` | `2026-03-28` |  |  |
| `q_promote_aiyingshi` | `promotion_review` | `acc_ays` | `retail_consumer` | `retail_multi_store` | `高` | `open` | `codex_llm` | 爱婴室属于当前 `L4` 中最接近高质量层的零售连锁样本之一。 | 判断是否先迁入主表 `L4`，并评估是否具备向 `L3` 上移基础。 | `第一批静态潜客种子池-v0.2` | `2026-03-28` |  |  |
| `q_promote_juewei` | `promotion_review` | `acc_juewei` | `retail_consumer` | `retail_chain_fnb` | `高` | `open` | `codex_llm` | 绝味已长期处于边界明确但证据略弱状态，适合进入迁移优先队列。 | 先迁 `L4`，并补连锁零售 vs 连锁餐饮画像边界证据。 | `第一批静态潜客种子池-v0.2` | `2026-03-28` |  |  |
| `q_promote_chabaidao` | `promotion_review` | `acc_chabaidao` | `retail_consumer` | `retail_chain_fnb` | `高` | `open` | `codex_llm` | 茶百道是连锁茶饮代表样本，当前应尽快完成 `L4` 迁移和后续上移判断。 | 迁入主表并补加盟扩张与区域经营证据。 | `第一批静态潜客种子池-v0.2` | `2026-03-28` |  |  |
| `q_promote_semir` | `promotion_review` | `acc_semir` | `retail_consumer` | `retail_multi_store` | `中` | `open` | `codex_llm` | 森马服饰零售网络清晰，但直营网 / 加盟结构和子品牌边界仍待补。 | 迁入主表后判断是否具备升至 `L3` 的基础。 | `第一批静态潜客种子池-v0.2` | `2026-03-28` |  |  |
| `q_promote_goertek` | `promotion_review` | `acc_goertek` | `advanced_manufacturing` | `mfg_multi_factory_group` | `高` | `open` | `codex_llm` | 歌尔是先进制造重要候选，具备明显多工厂 / 消费电子制造画像。 | 迁入主表并补官方经营复杂度证据，评估后续上移。 | `第一批静态潜客种子池-v0.2` | `2026-03-28` |  |  |
| `q_promote_lead` | `promotion_review` | `acc_lead` | `advanced_manufacturing` | `mfg_multi_factory_group` | `高` | `open` | `codex_llm` | 先导智能是先进制造主线的重要装备制造候选。 | 迁入主表并补全球化与多工厂复杂度证据。 | `第一批静态潜客种子池-v0.2` | `2026-03-28` |  |  |
| `q_promote_estun` | `promotion_review` | `acc_estun` | `advanced_manufacturing` | `mfg_rnd_sales_complex` | `中` | `open` | `codex_llm` | 埃斯顿方向成立，但经营协同与组织复杂度证据略弱。 | 迁入主表并补经营协同强证据。 | `第一批静态潜客种子池-v0.2` | `2026-03-28` |  |  |
| `q_boundary_711_mapping` | `boundary_review` |  | `retail_consumer` |  | `中` | `open` | `codex_llm` | 7-Eleven / 牛奶公司 / 惠康集团属于已知映射边界案例，后续作为知识资产时需要稳定 canonical 口径。 | 复核品牌、签约主体、集团归属三层映射并沉淀到映射知识资产。 | `客户案例与合作主体映射-v1.md` | `2026-03-28` |  |  |
| `q_boundary_group_brand_alias` | `boundary_review` |  |  |  | `中` | `open` | `codex_llm` | 后续批量迁移 `L5` 前，品牌名 / 主体名 / 集团名 alias 仍存在重复风险。 | 先做 alias 清单和 canonical 规则复核，避免主表漂移。 | `总池汇总视图-v0.7` | `2026-03-28` |  |  |
| `q_extract_chain_fnb_assets` | `knowledge_extraction` |  | `retail_consumer` | `retail_chain_fnb` | `高` | `open` | `codex_llm` | 当前零售消费已有多门店和高 SKU 资产，但连锁餐饮 / 茶饮 / 咖啡画像知识资产明显偏薄。 | 补抽茶百道、锅圈、周黑鸭、元祖等对应的连锁餐饮 / 餐饮零售知识资产。 | `knowledge_asset_registry_v1-首版真实内容-v0.1.md` | `2026-03-28` |  |  |
| `q_extract_cbec_supply_chain_assets` | `knowledge_extraction` |  | `cross_border_ecommerce` | `cbec_supply_chain_complex` | `中` | `open` | `codex_llm` | 复杂跨境经营画像当前有利润与 JTBD 资产，但供应链复杂度样本仍偏薄。 | 补抽赛维时代、华凯易佰、吉宏、子不语相关复杂跨境经营资产。 | `knowledge_asset_registry_v1-首版真实内容-v0.1.md` | `2026-03-28` |  |  |
| `q_extract_mfg_rnd_sales_assets` | `knowledge_extraction` |  | `advanced_manufacturing` | `mfg_rnd_sales_complex` | `中` | `open` | `codex_llm` | 先进制造已有价值流和驾驶舱资产，但研产销协同复杂画像的次级样本知识仍不足。 | 补抽迈瑞、联影、中航光电、德赛西威类样本的协同知识。 | `knowledge_asset_registry_v1-首版真实内容-v0.1.md` | `2026-03-28` |  |  |
| `q_cleanup_l5_retail_batch` | `cleanup_review` |  | `retail_consumer` |  | `高` | `open` | `codex_llm` | 后续批量迁移 `L5` 前，需要先清理零售消费主线中边界偏弱的放量候选。 | 先按画像稳定度和老客排除做一轮清池。 | `总池汇总视图-v0.7` | `2026-03-28` |  |  |
| `q_cleanup_l5_cbec_batch` | `cleanup_review` |  | `cross_border_ecommerce` |  | `高` | `open` | `codex_llm` | 跨境主线 `L5` 数量大，且品牌出海 / 供应链复杂两类画像边界容易漂。 | 先按品牌化程度、平台复杂度和老客排除复核。 | `总池汇总视图-v0.7` | `2026-03-28` |  |  |
| `q_cleanup_l5_mfg_batch` | `cleanup_review` |  | `advanced_manufacturing` |  | `高` | `open` | `codex_llm` | 先进制造 `L5` 中存在“泛制造”风险，需先按经营型 BI 切入边界清理。 | 先清理偏 MES/工厂控制导向、协同复杂度不够的对象。 | `总池汇总视图-v0.7` | `2026-03-28` |  |  |

## 3. 当前首版队列结构

当前首版队列已包含：

- `verification`
- `promotion_review`
- `boundary_review`
- `knowledge_extraction`
- `cleanup_review`

已满足“至少形成 4 类工作项”的阶段目标。

## 4. 下一步使用建议

1. 先处理 `promotion_review` 中的 `L4` 账户，配合主表 `v0.2` 迁移
2. 同步处理高优先级 `verification`，先为 `L1` 和最接近上移的 `L2/L3` 补第二条强证据
3. 在正式迁移大批 `L5` 之前，先完成三条 `cleanup_review`
4. 每月复盘时统计：
   - open 数量
   - resolved 数量
   - 各队列积压

## 5. 关联文档

- [account_review_queue_v1-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_review_queue_v1-字段模板-v1.md)
- [external_target_account_pool_v2-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.1.md)
- [knowledge_asset_registry_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/knowledge_asset_registry_v1-首版真实内容-v0.1.md)
