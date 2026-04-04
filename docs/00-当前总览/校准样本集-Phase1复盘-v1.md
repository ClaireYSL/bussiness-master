# 校准样本集-Phase1复盘-v1

## 1. 本轮范围

本轮已完成第一阶段 `15` 家样本的外部校准初判，覆盖：

- `零售消费` `5` 家
- `跨境电商` `5` 家
- `先进制造` `5` 家

对应结果文件：

- [calibration_batch_phase1_retail_v1.delegate.json](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/deliveries/calibration_batch_phase1_retail_v1.delegate.json)
- [calibration_batch_phase1_cbec_v1.delegate.json](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/deliveries/calibration_batch_phase1_cbec_v1.delegate.json)
- [calibration_batch_phase1_mfg_v1.delegate.json](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/deliveries/calibration_batch_phase1_mfg_v1.delegate.json)

---

## 2. 横向结论

### 2.1 主线判断

`15` 家中：

- `track keep`：`12`
- `track uncertain`：`3`

结论：

- 三条主线整体没有塌
- 当前更大的问题不在“主线彻底错了”
- 而在画像边界、最小事实、层级高估

### 2.2 画像判断

`15` 家中：

- `persona keep`：`8`
- `persona adjust`：`4`
- `persona uncertain`：`3`

结论：

- 画像是当前最明显的薄弱环节之一
- 特别是跨境和先进制造，存在“旧画像标签不在当前标准画像体系内”的问题

### 2.3 最小事实判断

`15` 家中：

- `pass`：`7`
- `partial`：`5`
- `fail`：`3`

结论：

- 当前系统不是“全都烂”
- 但只有不到一半样本真正通过了最小事实门
- 失败样本几乎都和核心字段缺失、官方来源不足直接相关

### 2.4 层级判断

`15` 家中：

- `maturity keep`：`9`
- `maturity downgrade`：`5`
- `maturity uncertain`：`1`

结论：

- 约三分之一样本已经被外部校准认为层级被高估
- 这说明“层级偏松”不是偶发，而是系统性问题

---

## 3. 三条主线分别看

## 3.1 零售消费

### 当前判断

- `4/5` 基本可保留
- `1/5` 明显失真

### 关键发现

- 名创优品、爱婴室、东鹏饮料相对稳
- 三只松鼠存在产品/服务描述模板化问题，但未被判明显高估
- 泡泡玛特缺少官方高可信来源，最小事实不成立，当前层级被高估

### 当前结论

- 零售消费这条线整体相对最稳
- 但 `L4/L5` 仍要看官方来源是否真的到位

## 3.2 跨境电商

### 当前判断

- `2/5` 稳
- `2/5` 需调整画像并降级
- `1/5` 最小事实失败

### 关键发现

- 安克、致欧较稳
- 吉宏、子不语都暴露出旧画像标签不在当前标准体系内的问题
- 乐歌核心字段缺失，最小事实失败，层级高估明显

### 当前结论

- 跨境电商不是主线错了
- 而是画像标准化和层级判断最明显偏松

## 3.3 先进制造

### 当前判断

- `2/5` 稳
- `2/5` 需要调整画像
- `1/5` 最小事实失败

### 关键发现

- 汇川、三一较稳
- 中微、博众的问题不在主线，而在 persona 不是当前标准画像
- 杰瑞核心字段缺失，最小事实失败，当前成熟度被高估

### 当前结论

- 先进制造主线整体还成立
- 但“技术型制造 / 多工厂制造 / 复杂经营协同”的标准画像边界还不够硬

---

## 4. 当前最明显的共性风险

按出现频次看，本轮最明显的风险是：

1. `persona_overreach`：`14`
2. `evidence_thin`：`10`
3. `generic_fact_risk`：`5`
4. `maturity_overrated`：`5`
5. `official_source_missing`：`4`

一句话总结：

- 当前系统最普遍的问题不是主线错误
- 而是画像边界偏松、证据偏薄、层级偏乐观

---

## 5. 本轮最重要的对象

### 5.1 可作为稳定锚点继续保留的对象

- `acc_miniso`
- `acc_anker`
- `acc_inovance`

### 5.2 可作为“升级成功样本”的对象

- `acc_eastroc`

说明：

- 东鹏饮料是本轮最明确的正向信号
- 外部校准认为其当前证据已足以从 `L5` 提到 `L3`

### 5.3 应优先降级或补证的对象

- `acc_popmart`
- `acc_loctek`
- `acc_jereh`

说明：

- 这三家分别对应零售、跨境、制造
- 且都落在当前最容易出问题的 `L4/L5`
- 它们可以直接作为“高估样本”反证集

---

## 6. 对系统设计的直接反馈

本轮结果已经足够支持以下判断：

### 6.1 知识主线暂时可保留

因为主线 `keep=12/15`，说明：

- 当前“知识库 -> 主线”这一层没有整体失效

### 6.2 画像体系需要收紧

因为 `persona adjust + uncertain = 7/15`，说明：

- 当前画像体系并没有稳定接住候选和上移判断

### 6.3 `L4/L5` 需要重新分流

因为多家 `L4/L5` 样本被判：

- 核心字段缺失
- 最小事实不成立
- 成熟度高估

所以：

- 当前 `L4/L5` 不能再被当成“只是薄一点”
- 必须重新区分正式候选和观察对象

---

## 7. 建议的下一步

基于这轮结果，下一步最合理的动作不是继续扩样本，而是先做 3 件事：

1. 对 `L4/L5` 增加正式候选 / 观察对象二次分流规则
2. 对当前标准画像做一轮收紧，尤其是跨境和先进制造
3. 直接把 `acc_popmart / acc_loctek / acc_jereh` 作为第一批“高估样本整改清单”

东鹏饮料则适合作为：

- 第一批“校准后可上移成功样本”

---

## 8. 当前结论

一句话总结：

- 第一轮校准已经证明：系统没有主线级崩塌，但画像边界、最小事实门槛和 `L4/L5` 层级口径都需要马上收紧
