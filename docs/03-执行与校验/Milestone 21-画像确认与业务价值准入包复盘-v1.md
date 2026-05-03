# Milestone 21-画像确认与业务价值准入包复盘-v1

## 摘要

- 输入对象：`30`
- M20 决策分布：`{'warn': 30}`
- 默认确认状态分布：`{'keep_pending_need_business_context': 30}`
- `confirm_active_high_value_count`：`0`

本包不写回工作簿。M21 的目的不是直接转 active，而是把画像确认和业务价值判断绑定起来。

## 准入规则

- 只有 `confirm_active_high_value` 可进入 M22 写回准入。
- 如果 `confirm_active_high_value_rate < 30%`，暂停 M22 写回，回到画像定义和候选选择策略。
- 真实写回仍需 baseline、gate、workbook integrity 和用户单独确认。

## 明细

### 杭可科技股份有限公司（acc_hangke）

- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `杭可科技股份有限公司` 是否值得围绕 `先进制造/mfg_multi_factory_group` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：已上移至 L2；后续继续补更强官方披露与字段级 evidence，但已达到高质量样本可复用标准。

### 汉钟精机股份有限公司（acc_hanzhong）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `汉钟精机股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务条线、客户协同与全球经营仍需补。

### 深圳市豪鹏科技股份有限公司（acc_haopeng）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `深圳市豪鹏科技股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务结构、客户协同与全球经营仍需补。

### 江苏恒立液压股份有限公司（acc_henglihyd）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `江苏恒立液压股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务条线、全球经营与客户结构仍需补。

### 深圳和而泰智能控制股份有限公司（acc_hetai）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `深圳和而泰智能控制股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：经营链路与组织颗粒度仍需补。

### 海目星激光科技集团股份有限公司（acc_hymson）

- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `海目星激光科技集团股份有限公司` 是否值得围绕 `先进制造/mfg_multi_factory_group` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：已上移至 L2；后续继续补更强官方披露与字段级 evidence，但已达到高质量样本可复用标准。

### 爱柯迪股份有限公司（acc_ikd）

- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `爱柯迪股份有限公司` 是否值得围绕 `先进制造/mfg_multi_factory_group` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：工厂布局、事业部结构与全球经营仍需补。

### 深圳市英威腾电气股份有限公司（acc_invt）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `深圳市英威腾电气股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务条线、组织复杂度与全球经营仍需补。

### 杰瑞石油服务集团股份有限公司（acc_jereh）

- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `杰瑞石油服务集团股份有限公司` 是否值得围绕 `先进制造/mfg_multi_factory_group` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：已上移至 L2；后续继续补更强官方披露与字段级 evidence，但已达到高质量样本可复用标准。

### 深圳市捷佳伟创新能源装备股份有限公司（acc_jiejia）

- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `深圳市捷佳伟创新能源装备股份有限公司` 是否值得围绕 `先进制造/mfg_multi_factory_group` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：工厂布局、业务条线与经营颗粒度仍需补。

### 江苏北人智能制造科技股份有限公司（acc_jsbr）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `江苏北人智能制造科技股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务结构、客户协同与全球经营仍需补。

### 深圳开立生物医疗科技股份有限公司（acc_kaili）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `深圳开立生物医疗科技股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：研产销协同链路与全球经营颗粒度仍需补。

### 深圳市科达利实业股份有限公司（acc_kedali）

- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `深圳市科达利实业股份有限公司` 是否值得围绕 `先进制造/mfg_multi_factory_group` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：工厂布局、事业部结构与全球经营仍需补。

### 深圳市徕芬电子科技有限公司（acc_laifen）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `深圳市徕芬电子科技有限公司` 是否值得围绕 `跨境电商/cbec_multi_platform_brand` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：海外平台结构、经营规模与组织颗粒度仍需补。

### 深圳市蓝禾技术有限公司（acc_lanhe）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `深圳市蓝禾技术有限公司` 是否值得围绕 `跨境电商/cbec_multi_platform_brand` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：海外经营规模与平台结构仍需补。

### 深圳市雷赛智能控制股份有限公司（acc_leisai）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `深圳市雷赛智能控制股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务条线、客户协同与全球经营仍需补。

### 慕容家居控股有限公司（acc_morhome）

- 主线/画像：`跨境电商` / `cbec_multi_platform_brand`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `慕容家居控股有限公司` 是否值得围绕 `跨境电商/cbec_multi_platform_brand` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：海外渠道、品牌矩阵与经营主体映射仍需补。

### 苏州纽威阀门股份有限公司（acc_neway）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `苏州纽威阀门股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：已基于公开披露补强与ICP校准上移至L2；后续继续补官网、年报、IR与字段级evidence，以评估是否进入L1锚点样本层。

### 瑞可达连接系统股份有限公司（acc_recodeal）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `瑞可达连接系统股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：组织复杂度与全球经营仍需补。

### 浙江日发精密机械股份有限公司（acc_rifa）

- 主线/画像：`先进制造` / `mfg_multi_factory_group`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `浙江日发精密机械股份有限公司` 是否值得围绕 `先进制造/mfg_multi_factory_group` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：工厂布局、业务条线与区域经营仍需补。

### 生益电子股份有限公司（acc_scc）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `生益电子股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：经营协同与客户结构仍需补。

### 沈阳芯源微电子设备股份有限公司（acc_scimee）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `沈阳芯源微电子设备股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：经营链路与组织复杂度仍需补。

### 浙江双环传动机械股份有限公司（acc_shuanghuan）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `浙江双环传动机械股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：全球经营与组织复杂度仍需补。

### 深圳拓邦股份有限公司（acc_topband）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `深圳拓邦股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：经营复杂度与多业务结构仍需补。

### 浙江万马股份有限公司（acc_wanma）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `浙江万马股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务结构、客户协同与经营颗粒度仍需补。

### 浙江伟星智能仪表股份有限公司（acc_weixingmeter）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `浙江伟星智能仪表股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：经营链路与组织协同颗粒度仍需补。

### 沪士电子股份有限公司（acc_wus）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `沪士电子股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务颗粒度与组织复杂度仍需补。

### 江苏亚威机床股份有限公司（acc_yawei）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `江苏亚威机床股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务结构、客户协同与全球经营仍需补。

### 浙江银轮机械股份有限公司（acc_yinlun）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `浙江银轮机械股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务结构、全球经营与客户协同颗粒度仍需补。

### 江苏鱼跃医疗设备股份有限公司（acc_yuyue）

- 主线/画像：`先进制造` / `mfg_rnd_sales_complex`
- M20 决策：`warn`
- warning codes：`['persona_boundary_unstable']`
- 默认确认状态：`keep_pending_need_business_context`
- 业务问题：请判断 `江苏鱼跃医疗设备股份有限公司` 是否值得围绕 `先进制造/mfg_rnd_sales_complex` 进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。
- 待补/风险：业务结构与制造协同仍需补。

## 下一步

1. 等 M23A 业务反馈回来后，更新本包 template。
2. 对 M21 的 30 家填写 `confirmation_status` 和业务价值字段。
3. 只有出现 `confirm_active_high_value` 时，生成 M22 写回准入包。
