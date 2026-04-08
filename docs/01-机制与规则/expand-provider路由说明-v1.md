# expand-provider路由说明-v1

## 目的

`expand` 入口不应再默认偏零售，而应先按主线 / 主画像分流，再判断是否存在匹配 provider。

## 当前脚本入口

- [expand_static_pool.py](/Users/clairaipartner/Codex/bussiness-master/scripts/expand_static_pool.py)

## 当前 provider 状态

### 已有专题 provider

- 零售消费 / 部分消费品画像
  - [expand_l5_consumer_personas_20260331.py](/Users/clairaipartner/Codex/bussiness-master/scripts/expand_l5_consumer_personas_20260331.py)

### 暂无稳定 provider

- 跨境电商
- 先进制造

## 路由规则

当前 `expand_static_pool.py` 先做：

1. 识别 `track`
2. 识别 `persona_id`
3. 从 `主线与画像注册表.xlsx` 中读取当前 `active` 业务画像
4. 判断该画像是否存在稳定 provider

如果有 provider：

- 输出 `provider_script`
- 输出 `provider_script` 模式
- 不再把脚本误路由到其他主线
- 未显式指定 `--output-file` 时，默认只写到 `/tmp/codex-static-pool-runs/`

如果没有 provider：

- 输出 `rule_driven_fallback`
- 明确说明需要进入规则驱动模式
- 不伪造“已成功扩池”

## 当前设计边界

这个入口脚本当前只是“路由层”，不是“全主线通用扩池引擎”。

因此它的目标是：

1. 纠正默认入口语义
2. 防止零售脚本误用于跨境 / 制造
3. 为后续新增 provider 预留统一入口

它当前不承诺：

1. 一次性补齐跨境扩池脚本
2. 一次性补齐制造扩池脚本
3. 自动执行所有 provider 的真实写回
