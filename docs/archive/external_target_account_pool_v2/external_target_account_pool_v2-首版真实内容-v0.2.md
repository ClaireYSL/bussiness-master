# `external_target_account_pool_v2` 首版真实内容 v0.2

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.1.md) 基础上，新增迁入当前 `L4=14` 家中可信候选。

这一步的目标不是把 `L4` 全部上移，而是先把它们正式纳入结构化主表，形成从 `59` 到 `73` 的主表覆盖。

## 2. 本轮迁移范围

### 已有基础

- `v0.1` 已迁入：
  - `L1=8`
  - `L2=36`
  - `L3=15`
  - 合计 `59`

### 本轮新增

- `L4=14`

### 本轮完成后

- 主表覆盖提升到 `73`

## 3. 字段策略

本轮 `L4` 迁移按最低入池字段执行，必填：

- `account_id`
- `account_canonical_name`
- `primary_track`
- `persona_tag`
- `pool_layer`
- `static_priority`
- `admission_reason_summary`
- `source_note`
- `validation_gap`

本轮可暂缓：

- `group_name`
- `secondary_jtbd`
- `dynamic_*`
- 详细 `knowledge_asset_refs`

## 4. 当前新增迁入的 L4 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_ays` | 上海爱婴室商务服务股份有限公司 | 爱婴室 | 零售消费 | 母婴零售 | 连锁零售 | retail_multi_store | L4 | A | 鲜丰水果,来伊份,博士眼镜 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 母婴零售连锁网络和门店经营特征明确，客观上符合多门店连锁零售画像。 | 第一批静态潜客种子池 v0.2 核验分层版 | 仍需补官方门店网络、区域经营与组织结构强证据。 |
| `acc_juewei` | 绝味食品股份有限公司 | 绝味鸭脖 | 零售消费 | 连锁食品零售 | 连锁零售 | retail_chain_fnb | L4 | B | 周黑鸭,来伊份 | 连锁经营分析平台 | ka_case_chatbi_frontline_v1 | 全国连锁网络与加盟经营属性明显，适合作为连锁餐饮 / 餐饮零售画像候选。 | 第一批静态潜客种子池 v0.2 核验分层版 | 主画像需继续压实，补加盟、区域和门店经营复杂度强证据。 |
| `acc_chabaidao` | 四川百茶百道实业股份有限公司 | 茶百道 | 零售消费 | 连锁茶饮 | 连锁餐饮 | retail_chain_fnb | L4 | A | 老乡鸡,周黑鸭,ChatBI 一线场景 | 连锁门店经营透视与一线问数 | ka_case_chatbi_frontline_v1 | 加盟连锁茶饮网络和区域扩张特征明确，客观上符合连锁餐饮 / 茶饮画像。 | 第一批静态潜客种子池 v0.2 核验分层版 | 需补加盟体系、区域经营和门店网络强证据。 |
| `acc_guoquan` | 锅圈食品（上海）股份有限公司 | 锅圈食汇 | 零售消费 | 餐饮零售 | 连锁零售 | retail_chain_fnb | L4 | B | 来伊份,周黑鸭 | 连锁经营分析与加盟体系分析 | ka_case_laiyifen_replenishment_v1 | 门店网络和餐饮零售混合经营特征成立，适合作为连锁餐饮 / 餐饮零售候选。 | 第一批静态潜客种子池 v0.2 核验分层版 | 零售 / 餐饮零售边界与加盟结构仍需压实。 |
| `acc_semir` | 浙江森马服饰股份有限公司 | 森马 / 巴拉巴拉 | 零售消费 | 鞋服零售 | 品牌零售 | retail_multi_store | L4 | A | 海澜之家,波司登,特步 | 鞋服零售经营分析 | ka_case_xianfeng_retail_v1 | 多品牌服饰零售与线下网络特征明确，客观上符合多门店零售画像。 | 第一批静态潜客种子池 v0.2 核验分层版 | 需补直营网 / 加盟结构和子品牌经营复杂度证据。 |
| `acc_popmart` | 北京泡泡玛特文化创意有限公司 | 泡泡玛特 | 零售消费 | 品牌零售 | 品牌零售 | retail_multi_store | L4 | B | 名创优品,晨光文具 | 品牌零售经营分析 | ka_case_xianfeng_retail_v1 | 品牌零售、门店网络和商品经营特征成立，适合作为品牌零售画像候选。 | 第一批静态潜客种子池 v0.2 核验分层版 | 中国经营主体、门店结构和商品分析切入证据仍需补。 |
| `acc_jihong` | 厦门吉宏科技股份有限公司 | 吉宏股份 | 跨境电商 | 跨境经营 | 供应链复杂跨境经营 | cbec_supply_chain_complex | L4 | B | 赛维时代,华凯易佰 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 跨境经营与供应链协同方向成立，客观上符合复杂跨境经营画像。 | 第一批静态潜客种子池 v0.2 核验分层版 | 需补跨境业务占比、平台结构和供应链复杂度强证据。 |
| `acc_zibuyu` | 子不语集团有限公司 | 子不语 | 跨境电商 | 跨境卖家 | 多平台卖家 | cbec_supply_chain_complex | L4 | B | 赛维时代,华凯易佰 | 多平台跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 服饰跨境与多平台经营方向成立，可作为复杂跨境经营画像候选。 | 第一批静态潜客种子池 v0.2 核验分层版 | 主体、组织结构与经营复杂度证据仍需补。 |
| `acc_goertek` | 歌尔股份有限公司 | 歌尔股份 | 先进制造 | 消费电子制造 | 多工厂制造 | mfg_multi_factory_group | L4 | A | 立讯精密,蓝思科技 | 多工厂经营驾驶舱 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 消费电子制造、多基地协同和全球经营方向明确，客观上符合多工厂制造画像。 | 第一批静态潜客种子池 v0.2 核验分层版 | 官方经营复杂度和多基地协同证据仍需补强。 |
| `acc_lead` | 无锡先导智能装备股份有限公司 | 先导智能 | 先进制造 | 装备制造 | 多工厂制造 | mfg_multi_factory_group | L4 | B | 海目星,杭可科技 | 多工厂经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 装备制造、全球化与复杂经营协同方向成立，符合多工厂制造画像。 | 第一批静态潜客种子池 v0.2 核验分层版 | 全球化与多工厂复杂度证据仍需补。 |
| `acc_estun` | 南京埃斯顿自动化股份有限公司 | 埃斯顿 | 先进制造 | 工业自动化 | 技术型制造 | mfg_rnd_sales_complex | L4 | B | 中控技术,汇川技术 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 工业自动化和技术型制造属性成立，可作为技术型制造画像候选。 | 第一批静态潜客种子池 v0.2 核验分层版 | 经营协同与组织复杂度强证据仍需补。 |
| `acc_bozon` | 博众精工科技股份有限公司 | 博众精工 | 先进制造 | 装备制造 | 技术型制造 | mfg_rnd_sales_complex | L4 | B | 海目星,先导智能 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 装备制造与复杂客户协同方向成立，可作为技术型制造画像候选。 | 第一批静态潜客种子池 v0.2 核验分层版 | LTC 链路和组织复杂度证据仍需补。 |
| `acc_maxwell` | 苏州迈为科技股份有限公司 | 迈为股份 | 先进制造 | 装备制造 | 技术型制造 | mfg_rnd_sales_complex | L4 | B | 先导智能,海目星 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 高端装备制造和复杂客户交付方向成立，适合作为技术型制造画像候选。 | 第二批扩展候选池 v0.2 首轮核验版 | 仍需补全球经营、组织结构和经营协同强证据。 |
| `acc_topstar` | 广东拓斯达科技股份有限公司 | 拓斯达 | 先进制造 | 自动化装备 | 技术型制造 | mfg_rnd_sales_complex | L4 | B | 机器人股份,中控技术 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 自动化装备与复杂经营协同方向成立，适合作为技术型制造画像候选。 | 第二批扩展候选池 v0.4 第三轮核验版 | 需补业务条线、客户结构与经营复杂度强证据。 |

## 5. 迁移后主表覆盖变化

### v0.1

- `L1=8`
- `L2=36`
- `L3=15`
- 合计 `59`

### v0.2

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- 合计 `73`

## 6. 下一步建议

1. 先为本轮迁入的 `L4` 账户各补 `1` 条最小证据记录
2. 从当前 `L4` 中优先处理：
   - 爱婴室
   - 茶百道
   - 歌尔
   - 先导智能
3. 然后再按主线分批迁移 `L5`

## 7. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.1.md)
- [external_target_account_pool_v2-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-字段模板-v1.md)
- [account_evidence_log_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_evidence_log_v1-首版真实内容-v0.1.md)
- [account_review_queue_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_review_queue_v1-首版真实内容-v0.1.md)
