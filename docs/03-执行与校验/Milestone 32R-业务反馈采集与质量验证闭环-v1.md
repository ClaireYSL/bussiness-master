# Milestone 32R-业务反馈采集与质量验证闭环-v1

## 摘要

- 抽样对象：`15`
- 已反馈：`0`
- 待反馈：`15`
- accepted/rejected/unclear：`0 / 0 / 0`
- 校验错误：`0`
- no-write proof：`True`

## 结论

- M32R 不伪造业务反馈；空反馈保持 pending。
- 本包不写工作簿、不写正式知识资产、不修改画像注册表。
- 当模板被业务侧填写后，重跑本脚本即可生成 accepted/rejected/unclear 统计和规则校准建议。

## 反馈采集对象

### 浙江哈尔斯真空器皿股份有限公司（acc_haers）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：浙江哈尔斯真空器皿股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002615

### 广东小熊电器股份有限公司（acc_bear）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：广东小熊电器股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002959

### 巴比食品集团有限公司（acc_babi）

- 主线/画像：`零售消费` / `retail_multi_store`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：中饮巴比食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=605338

### 广东拓斯达科技股份有限公司（acc_topstar）

- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：拓斯达科技股份有限公司具备制造组织、产品交付和经营协同特征，可用于验证 `mfg_multi_factory_group` 下的研产销协同和多基地/项目经营复杂度。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=300607

### 浙江海利得新材料股份有限公司（acc_hailide）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：浙江海利得新材料股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002206

### 华熙生物科技股份有限公司（acc_bloomage）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：华熙生物科技股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=688363

### 步步高商业连锁股份有限公司（acc_bbg）

- 主线/画像：`零售消费` / `retail_multi_store`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：步步高商业连锁股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002251

### 海象新材料股份有限公司（acc_haixiang）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：海象新材料股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=003011

### 光明乳业股份有限公司（acc_brightdairy）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：光明乳业股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=600597

### 中国黄金集团黄金珠宝股份有限公司（acc_chinagold）

- 主线/画像：`零售消费` / `retail_multi_store`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：中国黄金集团黄金珠宝股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=600916

### 江苏恒辉安防股份有限公司（acc_hengansecurity）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：江苏恒辉安防股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=300952

### 中顺洁柔纸业股份有限公司（acc_candr）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：中顺洁柔纸业股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002511

### 潮宏基珠宝股份有限公司（acc_chj）

- 主线/画像：`零售消费` / `retail_multi_store`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：潮宏基珠宝股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002345

### 恒林家居股份有限公司（acc_henglin）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：恒林家居股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=603661

### 中粮糖业控股股份有限公司（acc_cofco_sugar）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 反馈状态：`pending`，结果：`pending`
- 为什么匹配：中粮糖业控股股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
- 关键 evidence：https://www.cninfo.com.cn/new/disclosure/stock?stockCode=600737
