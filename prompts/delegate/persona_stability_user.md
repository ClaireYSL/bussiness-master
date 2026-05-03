请基于 Structured Input 对每家公司做主画像稳定性复核。

输出必须是 JSON object，结构如下：

{
  "batch_id": "milestone12_persona_stability_review_v1",
  "overall_summary": "一句话总结",
  "accounts": [
    {
      "account_id": "...",
      "account_name": "...",
      "current_persona": "...",
      "recommended_action": "keep_persona|change_persona|keep_pending_review|hold",
      "recommended_review_status": "active|pending_review|hold",
      "recommended_persona": "...",
      "confidence": "high|medium|low",
      "evidence_based_reason": "基于证据摘要的判断",
      "remaining_risk": "剩余风险或待补证点",
      "writeback_ready": false
    }
  ]
}

约束：

1. 不要把任何对象直接标成 writeback_ready=true，除非输入证据足以解释画像稳定且无关键风险。
2. 如果证据只支持公司业务存在，但不足以支持当前主画像，请使用 keep_pending_review。
3. 如果当前画像明显不匹配，请使用 change_persona 并给出 recommended_persona。
4. 如果公司边界、主体或业务明显不清，请使用 hold。
5. 不要输出 Markdown，只输出 JSON。
