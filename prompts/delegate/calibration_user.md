你正在参与“静态潜客池污染止血后的校准样本初判”。

请基于我提供的结构化输入，对每个样本对象做一轮保守初判。

任务要求：

1. 判断原 `primary_track` 是否仍成立
2. 判断原 `persona_tag` 是否仍成立
3. 判断当前最小事实是否成立
4. 判断原 `静态潜客记录成熟度` 是否可能被高估
5. 输出具体待补证点

你的判断必须完全基于输入中的：

1. 主线 / 画像定义
2. 冻结与可信最小字段集规范
3. 公司公开资料摘要
4. 当前结构化记录
5. evidence 摘要

不要使用输入外的原始源文件知识。

输出要求：

如果要求 `json`，请输出如下结构：

{
  "task_id": "",
  "samples": [
    {
      "account_id": "",
      "account_name": "",
      "track_assessment": {
        "status": "keep|adjust|uncertain",
        "reason": ""
      },
      "persona_assessment": {
        "status": "keep|adjust|uncertain",
        "reason": ""
      },
      "minimum_fact_assessment": {
        "status": "pass|partial|fail",
        "reason": ""
      },
      "maturity_assessment": {
        "status": "keep|downgrade|uncertain",
        "reason": "",
        "suggested_maturity": ""
      },
      "confidence_assessment": {
        "信息扎实度": "",
        "ICP匹配概率": ""
      },
      "evidence_gaps": [],
      "rewrite_suggestion": {
        "公司产品与服务概述": "",
        "商业模式概述": "",
        "admission_reason_summary": "",
        "validation_gap": ""
      },
      "risk_flags": []
    }
  ],
  "overall_findings": []
}

判定口径：

1. `track_assessment.status`
   - `keep`: 当前主线可被输入证据解释
   - `adjust`: 当前主线明显不稳，存在更合理候选
   - `uncertain`: 当前证据不足，不宜硬判

2. `persona_assessment.status`
   - `keep`: 当前画像与业务结构一致
   - `adjust`: 当前画像不稳或更像其他画像
   - `uncertain`: 当前证据不足，不宜硬判

3. `minimum_fact_assessment.status`
   - `pass`: 主体、产品服务、商业模式三项最小事实基本成立
   - `partial`: 只成立一部分
   - `fail`: 关键信息仍主要是模板化或不足

4. `maturity_assessment.status`
   - `keep`: 当前层级暂可保留
   - `downgrade`: 当前层级被高估
   - `uncertain`: 当前不能稳判

5. `risk_flags`
   可选值包括但不限于：
   - `generic_fact_risk`
   - `persona_overreach`
   - `track_boundary_risk`
   - `maturity_overrated`
   - `evidence_thin`
   - `official_source_missing`

写作要求：

1. `reason` 必须简短具体
2. `evidence_gaps` 必须是可执行补证项
3. `rewrite_suggestion` 必须保守，不得模板化夸大
4. 如果证据不足，`rewrite_suggestion` 宁可简短保守，也不要编
