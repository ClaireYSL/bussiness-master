# Milestone 22R-可信潜客写回准入材料复盘-v1

## 摘要

- 输入可信候选：`30`
- 写回准入候选：`30`
- fact patch：`30`
- queue patch：`30`
- 画像分布：`{'mfg_multi_factory_group': 7, 'mfg_rnd_sales_complex': 20, 'cbec_multi_platform_brand': 3}`
- 主线分布：`{'先进制造': 27, '跨境电商': 3}`
- report-only：`allow=30 / warn=0 / block=0`
- gate check：`PASS`
- 本轮真实写回：`false`

M22R 的职责是把 M21R 的可信画像匹配结果转成标准执行链路可验证的准入材料。它不是写回动作本身。

## 准入边界

- 只有 `trusted_match_ready` 会进入本包。
- 本包会生成 `review_status=active` 的 fact patch，用于 report-only 验证规则是否可放行。
- 真实工作簿写回必须另行获得用户确认，并使用 `--require-report-baseline`、gate check 和 workbook integrity。

## 候选明细

- `acc_hangke` 杭可科技股份有限公司：`先进制造` / `mfg_multi_factory_group`，证据 `2` 条，官方来源 `1` 个。
- `acc_hanzhong` 汉钟精机股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_haopeng` 深圳市豪鹏科技股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_henglihyd` 江苏恒立液压股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_hetai` 深圳和而泰智能控制股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_hymson` 海目星激光科技集团股份有限公司：`先进制造` / `mfg_multi_factory_group`，证据 `2` 条，官方来源 `1` 个。
- `acc_ikd` 爱柯迪股份有限公司：`先进制造` / `mfg_multi_factory_group`，证据 `2` 条，官方来源 `1` 个。
- `acc_invt` 深圳市英威腾电气股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_jereh` 杰瑞石油服务集团股份有限公司：`先进制造` / `mfg_multi_factory_group`，证据 `2` 条，官方来源 `1` 个。
- `acc_jiejia` 深圳市捷佳伟创新能源装备股份有限公司：`先进制造` / `mfg_multi_factory_group`，证据 `2` 条，官方来源 `1` 个。
- `acc_jsbr` 江苏北人智能制造科技股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_kaili` 深圳开立生物医疗科技股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_kedali` 深圳市科达利实业股份有限公司：`先进制造` / `mfg_multi_factory_group`，证据 `2` 条，官方来源 `1` 个。
- `acc_leisai` 深圳市雷赛智能控制股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_neway` 苏州纽威阀门股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_recodeal` 瑞可达连接系统股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_rifa` 浙江日发精密机械股份有限公司：`先进制造` / `mfg_multi_factory_group`，证据 `2` 条，官方来源 `1` 个。
- `acc_scc` 生益电子股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_scimee` 沈阳芯源微电子设备股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_shuanghuan` 浙江双环传动机械股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_topband` 深圳拓邦股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_wanma` 浙江万马股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_weixingmeter` 浙江伟星智能仪表股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_wus` 沪士电子股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_yawei` 江苏亚威机床股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_yinlun` 浙江银轮机械股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_yuyue` 江苏鱼跃医疗设备股份有限公司：`先进制造` / `mfg_rnd_sales_complex`，证据 `2` 条，官方来源 `1` 个。
- `acc_laifen` 深圳市徕芬电子科技有限公司：`跨境电商` / `cbec_multi_platform_brand`，证据 `2` 条，官方来源 `1` 个。
- `acc_lanhe` 深圳市蓝禾技术有限公司：`跨境电商` / `cbec_multi_platform_brand`，证据 `2` 条，官方来源 `1` 个。
- `acc_morhome` 慕容家居控股有限公司：`跨境电商` / `cbec_multi_platform_brand`，证据 `2` 条，官方来源 `1` 个。
