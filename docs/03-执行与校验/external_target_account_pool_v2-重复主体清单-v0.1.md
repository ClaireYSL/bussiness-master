# `external_target_account_pool_v2` 重复主体清单 v0.1

## 1. 文档目的

本文件用于锁定 `external_target_account_pool_v2` 当前已识别的重复 canonical account，并为去重治理提供统一决策依据。

说明：

- 这里的“重复”包括两类：
  - `同一 canonical_name` 被重复写入主表
  - `不同 account_id` 实际指向同一 canonical_name`
- 本清单只覆盖当前已识别并确认的重复主体

## 2. 当前结论

截至 [external_target_account_pool_v2-首版真实内容-v0.15.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/archive/external_target_account_pool_v2/external_target_account_pool_v2-首版真实内容-v0.15.md)，当前结构化主表共发现 `13` 组重复主体。

原始结构化覆盖量：`373`  
去重后的唯一主体数：`360`

## 3. 重复主体清单

| canonical_name | duplicate_account_ids | current_layers | current_sources | evidence_refs | queue_refs | recommended_primary_account_id | recommended_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 上海新阳半导体材料股份有限公司 | `acc_sinyang`, `acc_sinyang` | `L5`, `L5` | `v0.8`, `v0.12` | `ev_acc_sinyang_l5_intake` | 无独立 queue 影响 | `acc_sinyang` | 保留主记录，删除重复行 |
| 上海来伊份股份有限公司 | `acc_laiyifen`, `acc_laiyifen_legal` | `L5`, `L5` | `v0.3`, `v0.15` | `ev_acc_laiyifen_l5_intake`, `ev_acc_laiyifen_legal_l5_intake` | `q_v02_*` | `acc_laiyifen_legal` | 保留 legal 口径主记录，旧 id 合并 |
| 乐歌人体工学科技股份有限公司 | `acc_loctek`, `acc_loctek` | `L5`, `L5` | `v0.6`, `v0.12` | `ev_acc_loctek_l5_intake` | `q_v09_loctek_*` | `acc_loctek` | 保留主记录，删除重复行 |
| 匠心家居股份有限公司 | `acc_motern`, `acc_uxi` | `L5`, `L5` | `v0.7`, `v0.12` | `ev_acc_motern_l5_intake`, `ev_acc_uxi_l5_intake` | 无 | `acc_uxi` | 保留当前引用更多的主记录，旧 id 合并 |
| 广西柳工机械股份有限公司 | `acc_liugong`, `acc_liugong` | `L5`, `L5` | `v0.5`, `v0.12` | `ev_acc_liugong_l5_intake` | `q_v09_liugong_*` | `acc_liugong` | 保留主记录，删除重复行 |
| 江苏亚威机床股份有限公司 | `acc_yawei`, `acc_yawei` | `L5`, `L5` | `v0.9`, `v0.12` | `ev_acc_yawei_l5_intake` | 无 | `acc_yawei` | 保留主记录，删除重复行 |
| 沈阳新松机器人自动化股份有限公司 | `acc_siasun`, `acc_siasun` | `L2`, `L5` | `v0.1`, `v0.15` | `ev_acc_siasun_*` | `q_v12_siasun_verify`, `q_v12_robotics_gap` | `acc_siasun` | 保留高层级 `L2` 记录，删除 `L5` 重复行 |
| 浙江哈尔斯真空器皿股份有限公司 | `acc_haers`, `acc_haers` | `L5`, `L5` | `v0.6`, `v0.12` | `ev_acc_haers_l5_intake` | 无 | `acc_haers` | 保留主记录，删除重复行 |
| 浙江永强集团股份有限公司 | `acc_yotrio`, `acc_yotrio` | `L5`, `L5` | `v0.7`, `v0.12` | `ev_acc_yotrio_l5_intake` | 无 | `acc_yotrio` | 保留主记录，删除重复行 |
| 海欣食品股份有限公司 | `acc_haixinfood`, `acc_haixinfood` | `L5`, `L5` | `v0.5`, `v0.12` | `ev_acc_haixinfood_l5_intake` | 无 | `acc_haixinfood` | 保留主记录，删除重复行 |
| 深圳市杰美特科技股份有限公司 | `acc_jemet`, `acc_jame` | `L5`, `L5` | `v0.7`, `v0.12` | `ev_acc_jemet_l5_intake`, `ev_acc_jame_l5_intake` | `q_v04_*` | `acc_jame` | 保留规范化主记录，旧 id 合并 |
| 深圳市雷赛智能控制股份有限公司 | `acc_leisai`, `acc_leisai` | `L5`, `L5` | `v0.8`, `v0.12` | `ev_acc_leisai_l5_intake` | 无 | `acc_leisai` | 保留主记录，删除重复行 |
| 绝味食品股份有限公司 | `acc_juewei`, `acc_juewei` | `L4`, `L5` | `v0.2`, `v0.12` | `ev_acc_juewei_*` | `q_v01_*`, `q_v09_juewei_verify` | `acc_juewei` | 保留高层级 `L4` 记录，删除 `L5` 重复行 |

## 4. 处理原则摘要

本轮建议采用以下保留逻辑：

1. 同主体且层级不同：
   - 保留更高层级记录
2. 同主体且层级相同：
   - 优先保留命名更规范、下游引用更多的记录
3. 同主体且 account_id 相同：
   - 仅删除重复行，不涉及 id 合并
4. 旧 account_id 不物理删除：
   - 在 alias / merge 机制中保留映射关系

## 5. 关联文档

- [external_target_account_pool_v2-去重治理规则-v1.0.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/external_target_account_pool_v2-去重治理规则-v1.0.md)
- [external_target_account_pool_v2-清洗后事实主表-v1.0.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/02-注册表与结构/external_target_account_pool_v2-清洗后事实主表-v1.0.md)
