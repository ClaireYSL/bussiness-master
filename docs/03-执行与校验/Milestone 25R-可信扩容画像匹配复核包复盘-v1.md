# Milestone 25R-可信扩容画像匹配复核包复盘-v1

## 摘要

- 输入对象：`50`
- 可信状态分布：`{'trusted_match_ready': 50}`
- `trusted_match_ready_count`：`50`
- 官方证据覆盖率：`1.0`
- 核心信息完整率：`1.0`
- 入池理由清晰率：`1.0`

本包不执行写回。它用于把 M25R 的 `persona_boundary_unstable=50` 转成可信度状态。

## 边界

- `trusted_match_ready` 只表示可信潜客摘要/准入材料充分，不代表正式知识资产。
- 真实写回仍需用户单独确认。
- 潜客观察不得反向写入 knowledge_assets 或 persona_registry。

## 明细

### 拓斯达科技股份有限公司（acc_topstar）

- 可信状态：`trusted_match_ready`
- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- 匹配理由：拓斯达科技股份有限公司具备制造组织、产品交付和经营协同特征，可用于验证 `mfg_multi_factory_group` 下的研产销协同和多基地/项目经营复杂度。
- 核心产品/服务：拓斯达围绕工业机器人、注塑机辅机、数控机床和自动化应用系统开展研发、制造与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江哈尔斯真空器皿股份有限公司（acc_haers）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江哈尔斯真空器皿股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：哈尔斯围绕不锈钢真空保温器皿、杯壶产品和户外饮水器具开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江海利得新材料股份有限公司（acc_hailide）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江海利得新材料股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：海利得围绕涤纶工业长丝、塑胶材料、帘子布和新材料产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 海象新材料股份有限公司（acc_haixiang）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：海象新材料股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：海象新材围绕 PVC 地板、SPC 地板等新型环保地面材料开展研发、生产与出口销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 江苏恒辉安防股份有限公司（acc_hengansecurity）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：江苏恒辉安防股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：恒辉安防围绕安全防护手套、防护用品和功能性安全防护材料开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 恒林家居股份有限公司（acc_henglin）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：恒林家居股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：恒林家居围绕办公椅、沙发、按摩椅和健康坐具等家居产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江恒威电池股份有限公司（acc_hengwei）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江恒威电池股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：恒威电池围绕碱性电池、碳性电池和消费电池产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江恒林椅业股份有限公司（acc_hlin）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江恒林椅业股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：恒林椅业围绕办公椅、沙发、按摩椅和健康坐具等家居产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 深圳市杰美特科技股份有限公司（acc_jame）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：深圳市杰美特科技股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：杰美特围绕手机保护壳、智能终端配件和消费电子配件开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 朗科智能电气股份有限公司（acc_longood）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：朗科智能电气股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：朗科智能围绕智能控制器、电子电器控制组件和新能源控制产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江梦天木作家居有限公司（acc_mengtian_wood）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江梦天木作家居有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：梦天木作围绕木门、墙板、柜类和全屋定制木作产品开展设计、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江明新旭腾新材料股份有限公司（acc_mingxin）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江明新旭腾新材料股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：明新旭腾围绕汽车内饰新材料、天然皮革和功能复合材料开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江野马电池股份有限公司（acc_mustangbat）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江野马电池股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：野马电池围绕碱性电池、碳性电池和消费电池产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江正特股份有限公司（acc_patio）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江正特股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：正特股份围绕户外休闲家具、遮阳用品和庭院家具产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 深圳市赛维网络科技有限公司（acc_sailvan）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：深圳市赛维网络科技有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：赛维时代围绕跨境电商品牌运营、服饰配饰、家居和多品类自有品牌产品开展经营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 深圳市三态电子商务股份有限公司（acc_santai）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：深圳市三态电子商务股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：三态股份围绕跨境电商出口、供应链服务和多平台商品运营开展经营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江盛泰服装集团股份有限公司（acc_shengtai）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江盛泰服装集团股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：盛泰服装围绕针织面料、成衣制造和服装供应链服务开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 星徽股份有限公司（acc_skshu）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：星徽股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：星徽股份围绕跨境电商运营、滑轨铰链等五金产品和自有品牌出海开展经营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 泰鹏智能家居股份有限公司（acc_taipeng）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：泰鹏智能家居股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：泰鹏智能围绕庭院帐篷、户外休闲家具和智能家居用品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 永艺家具股份有限公司（acc_uechairs）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：永艺家具股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：永艺股份围绕办公椅、按摩椅、功能坐具和健康家具产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江华生科技股份有限公司（acc_washin）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江华生科技股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：华生科技围绕塑胶复合材料、气密材料和户外休闲材料开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 星华新材股份有限公司（acc_xinghua）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：星华新材股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：星华新材围绕反光材料、反光布和功能性复合材料开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江雅艺金属科技股份有限公司（acc_yayi）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江雅艺金属科技股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：雅艺科技围绕火盆、气炉、户外休闲家具和庭院用品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江永强集团股份有限公司（acc_yotrio）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江永强集团股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：永强集团围绕户外休闲家具、遮阳用品和庭院用品开展研发、生产与全球销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 深圳市有棵树科技股份有限公司（acc_youkeshu）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：深圳市有棵树科技股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：有棵树围绕跨境电商出口、供应链整合和多平台商品运营开展经营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 浙江正裕工业股份有限公司（acc_zhengyu）

- 可信状态：`trusted_match_ready`
- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 匹配理由：浙江正裕工业股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：正裕工业围绕汽车减震器、悬架系统零部件和汽车后市场产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 中饮巴比食品股份有限公司（acc_babi）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_multi_store`
- 匹配理由：中饮巴比食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：巴比食品围绕中式面点、速冻食品、团餐供应和连锁门店食品供应链开展经营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 步步高商业连锁股份有限公司（acc_bbg）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_multi_store`
- 匹配理由：步步高商业连锁股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：步步高围绕超市、百货、购物中心和区域零售连锁业务开展经营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 广东小熊电器股份有限公司（acc_bear）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：广东小熊电器股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：小熊电器围绕厨房小家电、生活小家电和创意家电产品开展研发、销售与品牌运营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 华熙生物科技股份有限公司（acc_bloomage）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：华熙生物科技股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：华熙生物围绕透明质酸、生物活性物和功能性护肤、食品健康产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 光明乳业股份有限公司（acc_brightdairy）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：光明乳业股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：光明乳业围绕乳制品、液态奶、酸奶、奶粉和冷链食品开展生产、销售与渠道运营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 中顺洁柔纸业股份有限公司（acc_candr）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：中顺洁柔纸业股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：中顺洁柔围绕生活用纸、护理用品和家庭清洁纸品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 中国黄金集团黄金珠宝股份有限公司（acc_chinagold）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_multi_store`
- 匹配理由：中国黄金集团黄金珠宝股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：中国黄金围绕黄金珠宝产品、投资金条和全国零售门店网络开展经营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 潮宏基珠宝股份有限公司（acc_chj）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_multi_store`
- 匹配理由：潮宏基珠宝股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：潮宏基围绕珠宝首饰、时尚配饰和零售门店网络开展设计、销售与品牌运营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 中粮糖业控股股份有限公司（acc_cofco_sugar）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：中粮糖业控股股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：中粮糖业围绕食糖、番茄制品、贸易和食品原料供应链开展生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 登康口腔护理用品股份有限公司（acc_dengkang）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：登康口腔护理用品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：登康口腔围绕牙膏、牙刷、漱口水和口腔护理用品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 欧亚集团股份有限公司（acc_eurasia）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_multi_store`
- 匹配理由：欧亚集团股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：欧亚集团围绕百货、购物中心、超市和区域商业零售网络开展经营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 福瑞达生物股份有限公司（acc_freda）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：福瑞达生物股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：福瑞达围绕化妆品、医药健康和生物科技产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 深圳市富安娜家居用品股份有限公司（acc_fuanna）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：深圳市富安娜家居用品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：富安娜围绕床上用品、家纺产品和家居生活用品开展设计、生产与零售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 盖世食品股份有限公司（acc_gaishi）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：盖世食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：盖世食品围绕预制凉菜、海洋食品和即食食品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 甘源食品股份有限公司（acc_ganyuan）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：甘源食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：甘源食品围绕坚果炒货、豆类零食和休闲食品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 广州酒家集团股份有限公司（acc_guangzhourestaurant）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_multi_store`
- 匹配理由：广州酒家集团股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：广州酒家围绕餐饮服务、月饼、速冻食品和食品制造开展经营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 乖宝宠物食品集团股份有限公司（acc_gubei）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：乖宝宠物食品集团股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：乖宝宠物围绕宠物食品、宠物零食和自有品牌宠物产品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 天津桂发祥十八街麻花食品股份有限公司（acc_guifaxiang）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：天津桂发祥十八街麻花食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：桂发祥围绕麻花、传统糕点和休闲食品开展生产、销售与品牌运营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 海欣食品股份有限公司（acc_haixinfood）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：海欣食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：海欣食品围绕速冻鱼糜制品、速冻肉制品和预制菜食品开展生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 好想你健康食品股份有限公司（acc_haoxiangni）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：好想你健康食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：好想你围绕红枣、坚果、健康食品和休闲食品开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 海融科技股份有限公司（acc_hiro）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：海融科技股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：海融科技围绕植脂奶油、烘焙原料和食品工业配料开展研发、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 好莱客创意家居股份有限公司（acc_holike）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_multi_store`
- 匹配理由：好莱客创意家居股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：好莱客围绕定制衣柜、橱柜、木门和全屋定制家居产品开展设计、生产与销售。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 红旗连锁股份有限公司（acc_hqls）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_multi_store`
- 匹配理由：红旗连锁股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：红旗连锁围绕便利超市、社区零售和区域门店网络开展经营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。

### 煌上煌集团食品股份有限公司（acc_huangshanghuang）

- 可信状态：`trusted_match_ready`
- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 匹配理由：煌上煌集团食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：煌上煌围绕酱卤肉制品、佐餐凉菜、米制品和连锁熟食门店开展生产、销售与品牌运营。
- 官方证据覆盖：`True`，证据数：`2`
- 风险/待补点：原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。
