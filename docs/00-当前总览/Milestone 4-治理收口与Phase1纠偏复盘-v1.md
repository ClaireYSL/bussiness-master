# Milestone 4-治理收口与Phase1纠偏复盘-v1

## 1. 本阶段定位

`Milestone 4` 的主目标不是继续扩池，也不是继续修档案，而是：

- 用 `Phase 1` 的 `15` 家校准样本，把治理收口正式落到规则、脚本和知识侧复核上

本阶段的核心动作是：

1. 收紧 `L4/L5`
2. 收紧标准 persona 集合
3. 输出 `15` 家样本正式纠偏结果
4. 复核 `learning_queue` 与这些样本的关系

---

## 2. 本阶段完成情况

### 2.1 规则层

已完成：

1. `L4/L5` 二次分流规则已正式写入 [L4L5二次分流与画像收紧方案-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/01-机制与规则/L4L5%E4%BA%8C%E6%AC%A1%E5%88%86%E6%B5%81%E4%B8%8E%E7%94%BB%E5%83%8F%E6%94%B6%E7%B4%A7%E6%96%B9%E6%A1%88-v1.md)
2. 主画像 / 次级画像 / 强相关知识资产引用的结构口径已固定
3. 标准 persona 集合与 legacy persona alias 已进入共享校验层

### 2.2 代码层

已完成：

1. `shared/static_pool/constants.py` 增加标准 persona 集合与 legacy persona alias map
2. `shared/static_pool/validators.py` 现可识别：
   - 非标准 persona
   - legacy persona
   - 次级画像不合规
   - `official_source_missing`
   - `minimum_fact fail`
3. `scripts/build_calibration_batch.py` 已带出：
   - `secondary_persona_tags`
   - `knowledge_asset_refs`
   - `talk_track_refs`
4. 新增 [build_phase1_rectification_package.py](/Users/clairaipartner/Codex/bussiness-master/scripts/build_phase1_rectification_package.py)，用于生成本轮正式纠偏结果包

### 2.3 样本层

已完成：

- `15/15` 样本正式纠偏结果已生成到 [phase1_rectification_package_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/phase1_rectification_package_v1.json)

横向结果：

- `formal_candidate = 11`
- `observation = 4`
- `downgrade = 5`
- `maturity_regraded = 9`
- `persona_adjusted = 7`
- `official_source_repair_needed = 4`

### 2.4 知识侧

已完成：

1. `learning_queue` 与 `Phase 1` 样本的关系复核
2. 当前 queued 项已分出：
   - 后续优先复核组
   - 保留待后续处理组
   - 占位组

参考文档：

- [learning_queue与Phase1样本关联复核-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/00-当前总览/learning_queue%E4%B8%8EPhase1%E6%A0%B7%E6%9C%AC%E5%85%B3%E8%81%94%E5%A4%8D%E6%A0%B8-v1.md)

---

## 3. 本阶段最关键的改变

### 3.1 `L4/L5` 不再只是“薄候选”

本阶段之后，`L4/L5` 的理解已经正式改变：

- 不是“只是信息少一点”
- 而是必须区分：
  - 正式候选
  - 观察对象

这直接解决了此前“高估对象也被包装成正式候选”的问题。

### 3.2 persona 不再允许自由漂移

本阶段之后：

- `persona_tag` 必须来自标准 persona 集合
- legacy persona 只能作为兼容映射存在
- 不再允许继续把历史 persona 直接写进正式判断层

### 3.3 强相关知识资产开始进入正式判断结果

本阶段之后：

- 强相关知识资产不再只是阅读层附属物
- 它已经进入：
  - 字段模板
  - 校准包
  - 正式纠偏结果包

---

## 4. 本阶段的代表性结果

### 4.1 高估整改样本

- `acc_popmart`
- `acc_loctek`
- `acc_jereh`

处理结果：

- 全部转为 `observation`
- 不再按正式候选继续推进

### 4.2 persona 重判样本

- `acc_jihong`
- `acc_zibuyu`
- `acc_amec`
- `acc_bozon`

处理结果：

- 已回到标准 persona 体系重判
- 必要时形成 “主画像 + 次级画像” 结果

### 4.3 正向锚点样本

- `acc_miniso`
- `acc_anker`
- `acc_inovance`

作用：

- 继续作为当前体系的稳定锚点

### 4.4 正向推进样本

- `acc_eastroc`

作用：

- 作为“校准后可正向推进”的样本

---

## 5. 仍未完成的部分

本阶段没有做这些事：

1. 没有做 `15` 家样本对应的工作簿真相源正式回写
2. 没有启动新一轮素材学习
3. 没有扫全量 `L4/L5` 存量
4. 没有做全量档案重修

这些都被明确留到后续阶段。

---

## 6. 下一阶段建议

如果沿着当前方向继续，下一阶段最自然的动作是：

1. 只对这 `15` 家样本做定向回写
2. 把 `observation` 与 `formal_candidate` 正式沉到事实源
3. 把标准 persona 集合正式映射到工作簿与档案层
4. 继续从本轮标出的 queued 优先组里做知识侧复核

---

## 7. 当前结论

一句话总结：

- `Milestone 4` 已经把“治理收口”从抽象讨论变成了可执行结果：规则更硬了、脚本更硬了、`15` 家样本不再漂着、知识侧也有了明确的下一步入口。
