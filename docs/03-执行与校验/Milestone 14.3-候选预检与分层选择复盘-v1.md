# Milestone 14.3-候选预检与分层选择复盘-v1

## 摘要

- 候选数：`15`
- 预检分层：`{'executable_now': 15}`
- 修复前决策：`{'block': 15}`
- 修复后决策：`{'allow': 15}`

## 分层结果

- `executable_now` `acc_aidi` 烟台艾迪精密机械股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_cnano` 江苏天奈科技股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_dingli` 浙江鼎力机械股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_focusprecision` 江苏先锋精密科技股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_haitianjg` 宁波海天精工股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_aukey` 深圳市傲基创新科技股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_cayi` 浙江嘉益保温科技股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_daziran` 浙江大自然户外用品股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_eccang` 深圳市易仓科技有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_greatstar` 杭州巨星科技股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_aimer` 爱慕股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_anji` 安记食品股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_anjingfood` 安井食品集团股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_aofei` 奥飞娱乐股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。
- `executable_now` `acc_arrowhome` 箭牌家居集团股份有限公司：可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。

## 后续选择规则

1. `executable_now` 可进入小批 report-only，但真实 write_back 仍需单独确认。
2. `needs_human_review` 可进入人工确认包或共享消费 pending 层。
3. `needs_patch` 不进入扩容执行批次，先补最小字段和官方来源。
4. `not_ready` 暂不纳入扩容，先回到画像或业务口径治理。
