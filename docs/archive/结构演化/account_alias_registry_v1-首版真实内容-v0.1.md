# `account_alias_registry_v1` 首版真实内容 v0.1

## 1. 文档目的

本文件记录当前去重治理中已经明确的 alias / merge 映射。

当前主要覆盖：

- 重复 account_id 合并
- 法人口径与历史口径合并

## 2. 首版 alias 记录

| alias_id | alias_name | canonical_account_id | canonical_name | alias_type | status | source_note | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `alias_laiyifen_old_id` | `acc_laiyifen` | `acc_laiyifen_legal` | 上海来伊份股份有限公司 | `duplicate_account_id` | `active` | 重复主体治理 v1.0 | 旧 id 并入 legal 口径主记录 |
| `alias_motern_old_id` | `acc_motern` | `acc_uxi` | 匠心家居股份有限公司 | `duplicate_account_id` | `active` | 重复主体治理 v1.0 | 旧 id 并入当前主记录 |
| `alias_jemet_old_id` | `acc_jemet` | `acc_jame` | 深圳市杰美特科技股份有限公司 | `duplicate_account_id` | `active` | 重复主体治理 v1.0 | 旧 id 并入当前主记录 |
| `alias_laiyifen_brand` | `来伊份` | `acc_laiyifen_legal` | 上海来伊份股份有限公司 | `brand_name` | `active` | 客户案例与合作主体映射 | 品牌名映射到 canonical account |
| `alias_uxi_brand` | `匠心家居` | `acc_uxi` | 匠心家居股份有限公司 | `brand_name` | `active` | 第十三批放量候选池 | 品牌名映射到 canonical account |
| `alias_jame_brand` | `杰美特` | `acc_jame` | 深圳市杰美特科技股份有限公司 | `brand_name` | `active` | 第十三批放量候选池 | 品牌名映射到 canonical account |

## 3. 当前用途

当前 alias 注册表主要用于：

1. 去重前比对
2. 历史 account_id 合并
3. 避免后续重复主体继续进入主表
