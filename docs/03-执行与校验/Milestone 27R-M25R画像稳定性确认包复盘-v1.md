# Milestone 27R-M25R画像稳定性确认包复盘-v1

## 摘要

- 输入对象：`50`
- 系统建议分布：`{'confirm_active_candidate': 50}`
- 待人工确认：`50`
- 知识资产写入：`False`

## 解释

- `confirm_active_candidate` 不是自动写回，也不是自动转 active。
- 它表示该对象已具备强来源、核心信息和可信画像匹配基础，可进入人工确认或 M28R report-only 准入。
- 本包不写入工作簿，不写入正式知识资产，不修改画像注册表。

## 明细

### 拓斯达科技股份有限公司（acc_topstar）

- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：拓斯达科技股份有限公司 是否应按 `mfg_multi_factory_group` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：拓斯达科技股份有限公司具备制造组织、产品交付和经营协同特征，可用于验证 `mfg_multi_factory_group` 下的研产销协同和多基地/项目经营复杂度。

### 浙江哈尔斯真空器皿股份有限公司（acc_haers）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江哈尔斯真空器皿股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江哈尔斯真空器皿股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江海利得新材料股份有限公司（acc_hailide）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江海利得新材料股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江海利得新材料股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 海象新材料股份有限公司（acc_haixiang）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：海象新材料股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：海象新材料股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 江苏恒辉安防股份有限公司（acc_hengansecurity）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：江苏恒辉安防股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：江苏恒辉安防股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 恒林家居股份有限公司（acc_henglin）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：恒林家居股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：恒林家居股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江恒威电池股份有限公司（acc_hengwei）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江恒威电池股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江恒威电池股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江恒林椅业股份有限公司（acc_hlin）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江恒林椅业股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江恒林椅业股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 深圳市杰美特科技股份有限公司（acc_jame）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：深圳市杰美特科技股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：深圳市杰美特科技股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 朗科智能电气股份有限公司（acc_longood）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：朗科智能电气股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：朗科智能电气股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江梦天木作家居有限公司（acc_mengtian_wood）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江梦天木作家居有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江梦天木作家居有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江明新旭腾新材料股份有限公司（acc_mingxin）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江明新旭腾新材料股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江明新旭腾新材料股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江野马电池股份有限公司（acc_mustangbat）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江野马电池股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江野马电池股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江正特股份有限公司（acc_patio）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江正特股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江正特股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 深圳市赛维网络科技有限公司（acc_sailvan）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：深圳市赛维网络科技有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：深圳市赛维网络科技有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 深圳市三态电子商务股份有限公司（acc_santai）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：深圳市三态电子商务股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：深圳市三态电子商务股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江盛泰服装集团股份有限公司（acc_shengtai）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江盛泰服装集团股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江盛泰服装集团股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 星徽股份有限公司（acc_skshu）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：星徽股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：星徽股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 泰鹏智能家居股份有限公司（acc_taipeng）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：泰鹏智能家居股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：泰鹏智能家居股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 永艺家具股份有限公司（acc_uechairs）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：永艺家具股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：永艺家具股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江华生科技股份有限公司（acc_washin）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江华生科技股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江华生科技股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 星华新材股份有限公司（acc_xinghua）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：星华新材股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：星华新材股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江雅艺金属科技股份有限公司（acc_yayi）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江雅艺金属科技股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江雅艺金属科技股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江永强集团股份有限公司（acc_yotrio）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江永强集团股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江永强集团股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 深圳市有棵树科技股份有限公司（acc_youkeshu）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：深圳市有棵树科技股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：深圳市有棵树科技股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 浙江正裕工业股份有限公司（acc_zhengyu）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：浙江正裕工业股份有限公司 是否应按 `cbec_multi_platform_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：浙江正裕工业股份有限公司具备产品供给、供应链协同和海外/多渠道经营特征，可用于验证 `cbec_multi_platform_brand` 下的跨境经营复杂度和商品运营链路。

### 中饮巴比食品股份有限公司（acc_babi）

- 主线/画像：`零售消费` / `retail_multi_store`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：中饮巴比食品股份有限公司 是否应按 `retail_multi_store` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：中饮巴比食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。

### 步步高商业连锁股份有限公司（acc_bbg）

- 主线/画像：`零售消费` / `retail_multi_store`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：步步高商业连锁股份有限公司 是否应按 `retail_multi_store` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：步步高商业连锁股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。

### 广东小熊电器股份有限公司（acc_bear）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：广东小熊电器股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：广东小熊电器股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 华熙生物科技股份有限公司（acc_bloomage）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：华熙生物科技股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：华熙生物科技股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 光明乳业股份有限公司（acc_brightdairy）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：光明乳业股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：光明乳业股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 中顺洁柔纸业股份有限公司（acc_candr）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：中顺洁柔纸业股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：中顺洁柔纸业股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 中国黄金集团黄金珠宝股份有限公司（acc_chinagold）

- 主线/画像：`零售消费` / `retail_multi_store`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：中国黄金集团黄金珠宝股份有限公司 是否应按 `retail_multi_store` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：中国黄金集团黄金珠宝股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。

### 潮宏基珠宝股份有限公司（acc_chj）

- 主线/画像：`零售消费` / `retail_multi_store`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：潮宏基珠宝股份有限公司 是否应按 `retail_multi_store` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：潮宏基珠宝股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。

### 中粮糖业控股股份有限公司（acc_cofco_sugar）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：中粮糖业控股股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：中粮糖业控股股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 登康口腔护理用品股份有限公司（acc_dengkang）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：登康口腔护理用品股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：登康口腔护理用品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 欧亚集团股份有限公司（acc_eurasia）

- 主线/画像：`零售消费` / `retail_multi_store`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：欧亚集团股份有限公司 是否应按 `retail_multi_store` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：欧亚集团股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。

### 福瑞达生物股份有限公司（acc_freda）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：福瑞达生物股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：福瑞达生物股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 深圳市富安娜家居用品股份有限公司（acc_fuanna）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：深圳市富安娜家居用品股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：深圳市富安娜家居用品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 盖世食品股份有限公司（acc_gaishi）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：盖世食品股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：盖世食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 甘源食品股份有限公司（acc_ganyuan）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：甘源食品股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：甘源食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 广州酒家集团股份有限公司（acc_guangzhourestaurant）

- 主线/画像：`零售消费` / `retail_multi_store`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：广州酒家集团股份有限公司 是否应按 `retail_multi_store` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：广州酒家集团股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。

### 乖宝宠物食品集团股份有限公司（acc_gubei）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：乖宝宠物食品集团股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：乖宝宠物食品集团股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 天津桂发祥十八街麻花食品股份有限公司（acc_guifaxiang）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：天津桂发祥十八街麻花食品股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：天津桂发祥十八街麻花食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 海欣食品股份有限公司（acc_haixinfood）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：海欣食品股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：海欣食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 好想你健康食品股份有限公司（acc_haoxiangni）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：好想你健康食品股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：好想你健康食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 海融科技股份有限公司（acc_hiro）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：海融科技股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：海融科技股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。

### 好莱客创意家居股份有限公司（acc_holike）

- 主线/画像：`零售消费` / `retail_multi_store`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：好莱客创意家居股份有限公司 是否应按 `retail_multi_store` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：好莱客创意家居股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。

### 红旗连锁股份有限公司（acc_hqls）

- 主线/画像：`零售消费` / `retail_multi_store`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：红旗连锁股份有限公司 是否应按 `retail_multi_store` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：红旗连锁股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_multi_store` 下的商品、渠道和零售经营复杂度。

### 煌上煌集团食品股份有限公司（acc_huangshanghuang）

- 主线/画像：`零售消费` / `retail_high_sku_brand`
- 系统建议：`confirm_active_candidate`，置信度：`high`
- 边界问题：煌上煌集团食品股份有限公司 是否应按 `retail_high_sku_brand` 进入 L3 可消费池？如果不是，应调整画像、继续 pending，还是 hold？
- 匹配理由：煌上煌集团食品股份有限公司具备消费品、门店/渠道或高 SKU 经营特征，可用于验证 `retail_high_sku_brand` 下的商品、渠道和零售经营复杂度。
