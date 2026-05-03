# Milestone 30R-写回后50家可消费池复核与业务抽样评估-v1

## 摘要

- 写回对象：`50`
- L3 可消费对象：`50`
- 仍需修复对象：`0`
- 抽样对象：`15`
- 画像分布：`{'retail_multi_store': 8, 'retail_high_sku_brand': 16, 'cbec_multi_platform_brand': 25, 'mfg_multi_factory_group': 1}`
- 工作簿完整性：`True`
- M28R 写回：`promoted=50 / skipped=0`

## 结论

- M30R 不做写回，只做写回后产品化复核和业务抽样准备。
- 这一步的核心问题不是“还能不能跑”，而是“这 50 家是否真能被业务侧读懂、判断、反馈”。
- 潜客观察仍不能直接进入正式知识资产，只能形成业务反馈、source gap 或规则校准建议。

## 抽样评估清单

### 浙江哈尔斯真空器皿股份有限公司（acc_haers）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 抽样原因：画像 `cbec_multi_platform_brand` 代表样本
- 为什么匹配：浙江哈尔斯真空器皿股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：哈尔斯围绕不锈钢真空保温器皿、杯壶产品和户外饮水器具开展研发、生产与销售。
- 经营结构：浙江哈尔斯真空器皿股份有限公司以产品研发/供应链组织、海外渠道或多平台运营为核心，围绕商品规划、供应链协同和线上销售组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002615

### 广东小熊电器股份有限公司（acc_bear）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 抽样原因：画像 `retail_high_sku_brand` 代表样本
- 为什么匹配：广东小熊电器股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：小熊电器围绕厨房小家电、生活小家电和创意家电产品开展研发、销售与品牌运营。
- 经营结构：广东小熊电器股份有限公司以消费品牌、产品研发、渠道分销和零售终端运营为核心，围绕 SKU 管理、渠道供给和品牌增长组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002959

### 巴比食品集团有限公司（acc_babi）

- 主线/画像：`零售消费` / `retail_multi_store`
- 抽样原因：画像 `retail_multi_store` 代表样本
- 为什么匹配：中饮巴比食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：巴比食品围绕中式面点、速冻食品、团餐供应和连锁门店食品供应链开展经营。
- 经营结构：中饮巴比食品股份有限公司以品牌商品、门店网络、渠道运营和供应链补货为核心，围绕区域经营、商品管理和会员/渠道运营组织业务。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=605338

### 广东拓斯达科技股份有限公司（acc_topstar）

- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- 抽样原因：画像 `mfg_multi_factory_group` 代表样本
- 为什么匹配：拓斯达科技股份有限公司具备制造组织、产品交付和经营协同特征，可用于验证 `mfg_multi_factory_group` 下的研产销协同和多基地/项目经营复杂度。
- 核心产品/服务：拓斯达围绕工业机器人、注塑机辅机、数控机床和自动化应用系统开展研发、制造与销售。
- 经营结构：拓斯达科技股份有限公司以技术研发、制造交付、供应链协同和客户项目服务为核心组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=300607

### 浙江海利得新材料股份有限公司（acc_hailide）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 抽样原因：画像 `cbec_multi_platform_brand` 分层抽样
- 为什么匹配：浙江海利得新材料股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：海利得围绕涤纶工业长丝、塑胶材料、帘子布和新材料产品开展研发、生产与销售。
- 经营结构：浙江海利得新材料股份有限公司以产品研发/供应链组织、海外渠道或多平台运营为核心，围绕商品规划、供应链协同和线上销售组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002206

### 华熙生物科技股份有限公司（acc_bloomage）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 抽样原因：画像 `retail_high_sku_brand` 分层抽样
- 为什么匹配：华熙生物科技股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：华熙生物围绕透明质酸、生物活性物和功能性护肤、食品健康产品开展研发、生产与销售。
- 经营结构：华熙生物科技股份有限公司以消费品牌、产品研发、渠道分销和零售终端运营为核心，围绕 SKU 管理、渠道供给和品牌增长组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=688363

### 步步高商业连锁股份有限公司（acc_bbg）

- 主线/画像：`零售消费` / `retail_multi_store`
- 抽样原因：画像 `retail_multi_store` 分层抽样
- 为什么匹配：步步高商业连锁股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：步步高围绕超市、百货、购物中心和区域零售连锁业务开展经营。
- 经营结构：步步高商业连锁股份有限公司以品牌商品、门店网络、渠道运营和供应链补货为核心，围绕区域经营、商品管理和会员/渠道运营组织业务。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002251

### 海象新材料股份有限公司（acc_haixiang）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 抽样原因：画像 `cbec_multi_platform_brand` 分层抽样
- 为什么匹配：海象新材料股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：海象新材围绕 PVC 地板、SPC 地板等新型环保地面材料开展研发、生产与出口销售。
- 经营结构：海象新材料股份有限公司以产品研发/供应链组织、海外渠道或多平台运营为核心，围绕商品规划、供应链协同和线上销售组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=003011

### 光明乳业股份有限公司（acc_brightdairy）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 抽样原因：画像 `retail_high_sku_brand` 分层抽样
- 为什么匹配：光明乳业股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：光明乳业围绕乳制品、液态奶、酸奶、奶粉和冷链食品开展生产、销售与渠道运营。
- 经营结构：光明乳业股份有限公司以消费品牌、产品研发、渠道分销和零售终端运营为核心，围绕 SKU 管理、渠道供给和品牌增长组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=600597

### 中国黄金集团黄金珠宝股份有限公司（acc_chinagold）

- 主线/画像：`零售消费` / `retail_multi_store`
- 抽样原因：画像 `retail_multi_store` 分层抽样
- 为什么匹配：中国黄金集团黄金珠宝股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：中国黄金围绕黄金珠宝产品、投资金条和全国零售门店网络开展经营。
- 经营结构：中国黄金集团黄金珠宝股份有限公司以品牌商品、门店网络、渠道运营和供应链补货为核心，围绕区域经营、商品管理和会员/渠道运营组织业务。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=600916

### 江苏恒辉安防股份有限公司（acc_hengansecurity）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 抽样原因：画像 `cbec_multi_platform_brand` 分层抽样
- 为什么匹配：江苏恒辉安防股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：恒辉安防围绕安全防护手套、防护用品和功能性安全防护材料开展研发、生产与销售。
- 经营结构：江苏恒辉安防股份有限公司以产品研发/供应链组织、海外渠道或多平台运营为核心，围绕商品规划、供应链协同和线上销售组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=300952

### 中顺洁柔纸业股份有限公司（acc_candr）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 抽样原因：画像 `retail_high_sku_brand` 分层抽样
- 为什么匹配：中顺洁柔纸业股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：中顺洁柔围绕生活用纸、护理用品和家庭清洁纸品开展研发、生产与销售。
- 经营结构：中顺洁柔纸业股份有限公司以消费品牌、产品研发、渠道分销和零售终端运营为核心，围绕 SKU 管理、渠道供给和品牌增长组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002511

### 潮宏基珠宝股份有限公司（acc_chj）

- 主线/画像：`零售消费` / `retail_multi_store`
- 抽样原因：画像 `retail_multi_store` 分层抽样
- 为什么匹配：潮宏基珠宝股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：潮宏基围绕珠宝首饰、时尚配饰和零售门店网络开展设计、销售与品牌运营。
- 经营结构：潮宏基珠宝股份有限公司以品牌商品、门店网络、渠道运营和供应链补货为核心，围绕区域经营、商品管理和会员/渠道运营组织业务。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002345

### 恒林家居股份有限公司（acc_henglin）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 抽样原因：画像 `cbec_multi_platform_brand` 分层抽样
- 为什么匹配：恒林家居股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 核心产品/服务：恒林家居围绕办公椅、沙发、按摩椅和健康坐具等家居产品开展研发、生产与销售。
- 经营结构：恒林家居股份有限公司以产品研发/供应链组织、海外渠道或多平台运营为核心，围绕商品规划、供应链协同和线上销售组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=603661

### 中粮糖业控股股份有限公司（acc_cofco_sugar）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 抽样原因：画像 `retail_high_sku_brand` 分层抽样
- 为什么匹配：中粮糖业控股股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 核心产品/服务：中粮糖业围绕食糖、番茄制品、贸易和食品原料供应链开展生产与销售。
- 经营结构：中粮糖业控股股份有限公司以消费品牌、产品研发、渠道分销和零售终端运营为核心，围绕 SKU 管理、渠道供给和品牌增长组织经营。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=600737

## 下一步

1. 业务/研究侧填写抽样评估模板。
2. 汇总 `worth_following`、`recommended_next_action` 和 `disqualify_reason`。
3. 只把反馈沉淀为候选观察和规则校准建议，不直接改写正式知识资产。
