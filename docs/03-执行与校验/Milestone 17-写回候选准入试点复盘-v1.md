# Milestone 17-写回候选准入试点复盘-v1

## 摘要

- allow 候选：`15`
- gate：`PASS`
- 本轮真实写回：`True`
- 建议动作：M17 已完成真实写回；下一步进入写回后复核和 M18 运营化。

## 候选清单

- `acc_aidi` 烟台艾迪精密机械股份有限公司：`mfg_rnd_sales_complex`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_aimer` 爱慕股份有限公司：`retail_high_sku_brand`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_anji` 安记食品股份有限公司：`retail_high_sku_brand`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_anjingfood` 安井食品集团股份有限公司：`retail_high_sku_brand`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_aofei` 奥飞娱乐股份有限公司：`retail_high_sku_brand`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_arrowhome` 箭牌家居集团股份有限公司：`retail_multi_store`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_aukey` 深圳市傲基创新科技股份有限公司：`cbec_multi_platform_brand`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_cayi` 浙江嘉益保温科技股份有限公司：`cbec_multi_platform_brand`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_cnano` 江苏天奈科技股份有限公司：`mfg_rnd_sales_complex`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_daziran` 浙江大自然户外用品股份有限公司：`cbec_multi_platform_brand`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_dingli` 浙江鼎力机械股份有限公司：`mfg_multi_factory_group`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_eccang` 深圳市易仓科技有限公司：`cbec_multi_platform_brand`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_focusprecision` 江苏先锋精密科技股份有限公司：`mfg_rnd_sales_complex`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_greatstar` 杭州巨星科技股份有限公司：`cbec_multi_platform_brand`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。
- `acc_haitianjg` 宁波海天精工股份有限公司：`mfg_multi_factory_group`，patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。

## 安全边界

- 本包只证明这些对象在 patch 叠加后具备写回准入，不自动修改工作簿。
- 若用户确认真实写回，必须使用现有 baseline 与 `--require-report-baseline`，并在写回后重新执行 workbook integrity。
