# Milestone 25R-可信扩容预检复盘-v1

## 摘要

- 预检候选：`50`
- 分层：`{'needs_patch': 50}`
- report-only：`not_run_pre_patch_required`
- 来源治理前置：`True`

## 结论

- 本轮只做扩容预检，不生成伪 fact patch。
- 下一步应先补官方来源和最小核心字段，再执行 enrich/promote report-only。
- 本轮未执行真实 write_back。

## 候选清单

- `needs_patch` `acc_topstar` 拓斯达科技股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_haers` 浙江哈尔斯真空器皿股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_hailide` 浙江海利得新材料股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_haixiang` 海象新材料股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_hengansecurity` 江苏恒辉安防股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_henglin` 恒林家居股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_hengwei` 浙江恒威电池股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_hlin` 浙江恒林椅业股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_jame` 深圳市杰美特科技股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_longood` 朗科智能电气股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_mengtian_wood` 浙江梦天木作家居有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_mingxin` 浙江明新旭腾新材料股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_mustangbat` 浙江野马电池股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_patio` 浙江正特股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_sailvan` 深圳市赛维网络科技有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_santai` 深圳市三态电子商务股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_shengtai` 浙江盛泰服装集团股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_skshu` 星徽股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_taipeng` 泰鹏智能家居股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_uechairs` 永艺家具股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_washin` 浙江华生科技股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_xinghua` 星华新材股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_yayi` 浙江雅艺金属科技股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_yotrio` 浙江永强集团股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_youkeshu` 深圳市有棵树科技股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_zhengyu` 浙江正裕工业股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_babi` 中饮巴比食品股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_babi` 巴比食品集团有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_bbg` 步步高商业连锁股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_bear` 广东小熊电器股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_bloomage` 华熙生物科技股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_brightdairy` 光明乳业股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_candr` 中顺洁柔纸业股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_chinagold` 中国黄金集团黄金珠宝股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_chj` 潮宏基珠宝股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_cofco_sugar` 中粮糖业控股股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_dengkang` 登康口腔护理用品股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_eurasia` 欧亚集团股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_freda` 福瑞达生物股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_fuanna` 深圳市富安娜家居用品股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_gaishi` 盖世食品股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_ganyuan` 甘源食品股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_guangzhourestaurant` 广州酒家集团股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_gubei` 乖宝宠物食品集团股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_guifaxiang` 天津桂发祥十八街麻花食品股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_haixinfood` 海欣食品股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_haoxiangni` 好想你健康食品股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_hiro` 海融科技股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_holike` 好莱客创意家居股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
- `needs_patch` `acc_hqls` 红旗连锁股份有限公司：需补 `admission_reason_summary,official_or_high_confidence_source,公司产品与服务概述,商业模式概述`
