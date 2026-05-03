# Milestone 16-迁移交接自检复盘-v1

- 生成时间：`2026-04-28T14:18:39.046950+00:00`
- 总结论：`PASS`

## 检查项

- workbook_integrity：`PASS`
- env：`PASS`
- source_tag_guard：`PASS`
- py_compile：`PASS`
- m13_rule_package：`PASS`
- m14_report_only：`PASS`
- m14_2_report_only：`PASS`
- m14_2_gate_check：`PASS`
- m14_3_preflight：`PASS`
- m15_2_share_package：`PASS`
- m17_admission_package：`PASS`
- m18_operational_package：`PASS`
- m19_feedback_package：`PASS`
- m20_batch_intake：`PASS`
- m23a_business_feedback_package：`PASS`
- m21_persona_business_confirmation_package：`PASS`
- m21r_trusted_match_review：`PASS`
- m22r_trusted_writeback_admission：`PASS`
- m23r_trusted_prospect_summary：`PASS`
- m24r_knowledge_source_governance：`PASS`
- m25r_expansion_preflight：`PASS`
- m25r_expansion_intake_patch_report_only：`PASS`
- m25r_trusted_expansion_review：`PASS`

## 当前里程碑摘要

- M13：`{'account_count': 12, 'decision_counts': {'keep_pending_review': 12}, 'strong_evidence_total': 24, 'active_candidate_count': 0, 'keep_pending_review_count': 12, 'hold_review_count': 0}`
- M14：`{'allow': 0, 'warn': 0, 'block': 15}`
- M14.2：`{'allow': 0, 'warn': 15, 'block': 0}`
- M14.3：`{'candidate_count': 15, 'preflight_status_counts': {'executable_now': 15}, 'before_decision_counts': {'block': 15}, 'after_decision_counts': {'allow': 15}}`
- M15.2：`{'item_count': 27, 'share_status_counts': {'high_value_pending': 12, 'ready_for_human_review': 15}, 'share_ready_or_pending': 27, 'not_share_ready': 0, 'ready_for_human_review': 15, 'high_value_pending': 12, 'needs_intake_patch': 0}`
- M17：`{'allow_candidate_count': 15, 'decision_counts': {'allow': 15}, 'gate_ok': True, 'writeback_executed': True, 'promoted': 15, 'skipped': 0, 'recommended_action': 'M17 已完成真实写回；下一步进入写回后复核和 M18 运营化。'}`
- M18：`{'account_count': 15, 'share_status_counts': {'l3_share_ready': 15}, 'share_ready_count': 15, 'needs_fix_count': 0, 'workbook_integrity_ok': True, 'm17_promoted': 15, 'm17_skipped': 0}`
- M19：`{'feedback_item_count': 15, 'next_candidate_count': 134, 'candidate_status_counts': {'needs_intake_patch': 106, 'not_ready': 28}, 'candidate_decision_counts': {'block': 134}}`
- M20：`{'allow': 0, 'warn': 30, 'block': 0}`
- M23A：`{'account_count': 15, 'share_ready_count': 15, 'business_reviewed_count': 0, 'accepted_by_business_count': 0, 'rejected_by_business_count': 0, 'next_action_defined_count': 0, 'positive_fit_rate': None, 'feedback_status_counts': {'pending_business_feedback': 15}}`
- M21：`{'account_count': 30, 'm20_decision_counts': {'warn': 30}, 'default_confirmation_status_counts': {'keep_pending_need_business_context': 30}, 'confirm_active_high_value_count': 0, 'confirm_active_high_value_rate': 0.0, 'business_reviewed_count': 0, 'next_action_defined_count': 0}`
- M21R：`{'account_count': 30, 'trusted_status_counts': {'trusted_match_ready': 30}, 'trusted_match_ready_count': 30, 'profile_match_pending_count': 0, 'evidence_pending_count': 0, 'persona_adjust_needed_count': 0, 'not_icp_count': 0, 'official_evidence_coverage_rate': 1.0, 'core_info_complete_rate': 1.0, 'admission_reason_clear_rate': 1.0}`
- M22R：`{'trusted_input_count': 30, 'admission_candidate_count': 30, 'fact_patch_count': 30, 'queue_patch_count': 30, 'skipped_count': 0, 'report_only_allow': 30, 'report_only_warn': 0, 'report_only_block': 0, 'report_only_result_count': 30, 'gate_ok': True, 'track_counts': {'先进制造': 27, '跨境电商': 3}, 'persona_counts': {'mfg_multi_factory_group': 7, 'mfg_rnd_sales_complex': 20, 'cbec_multi_platform_brand': 3}}`
- M23R：`{'card_count': 30, 'strong_evidence_card_count': 30, 'missing_strong_evidence_count': 0, 'missing_strong_evidence_account_ids': [], 'trusted_status_counts': {'trusted_match_ready': 30}, 'persona_counts': {'mfg_multi_factory_group': 7, 'mfg_rnd_sales_complex': 20, 'cbec_multi_platform_brand': 3}, 'track_counts': {'先进制造': 27, '跨境电商': 3}, 'sales_action_terms_detected': False, 'formal_knowledge_write_enabled': False, 'gate_ok': True}`
- M24R：`{'candidate_observation_count': 30, 'source_gap_count': 3, 'rule_calibration_proposal_count': 3, 'learning_queue_task_count': 3, 'persona_counts': {'mfg_multi_factory_group': 7, 'mfg_rnd_sales_complex': 20, 'cbec_multi_platform_brand': 3}, 'formal_knowledge_write_enabled': False, 'no_write_proof_ok': True}`
- M25R：`{'candidate_count': 50, 'target_size': 50, 'preflight_status_counts': {'needs_patch': 50}, 'track_counts': {'先进制造': 1, '跨境电商': 25, '零售消费': 24}, 'persona_counts': {'mfg_multi_factory_group': 1, 'cbec_brand_outbound': 2, 'cbec_supply_chain_complex': 22, 'cbec_multi_platform_brand': 1, 'retail_multi_store_chain': 1, 'retail_chain_fnb': 2, 'retail_multi_store': 6, 'retail_high_sku_brand': 15}, 'source_governance_ok': True, 'report_only_status': 'not_run_pre_patch_required', 'report_only_run_summary_file': '', 'gate_check_file': '', 'true_writeback_executed': False}`
- M25R_patch：`{'account_count': 50, 'skipped_count': 81, 'official_source_ready_count': 50, 'evidence_row_count': 100, 'source_type_counts': {'cninfo': 49, 'structured_intake_patch': 50, 'official_website': 1}, 'report_only_allow': 0, 'report_only_warn': 50, 'report_only_block': 0, 'report_only_result_count': 50, 'gate_ok': True, 'trusted_match_ready_count': 50, 'trusted_review_count': 50}`
- M25R_review：`{'account_count': 50, 'trusted_status_counts': {'trusted_match_ready': 50}, 'trusted_match_ready_count': 50, 'profile_match_pending_count': 0, 'evidence_pending_count': 0, 'persona_adjust_needed_count': 0, 'not_icp_count': 0, 'official_evidence_coverage_rate': 1.0, 'core_info_complete_rate': 1.0, 'admission_reason_clear_rate': 1.0}`

## 接力建议

1. 当前仍不执行真实 write_back；M22R 只完成可信潜客写回准入材料。
2. M23A/M21 业务反馈类产物仅作为可读性参考，不作为主写回准入依据。
3. 若要真实写回 30 家，必须由用户单独确认，并使用 M22R baseline + `--require-report-baseline`。
4. M24R 只能做知识资产来源治理与潜客观察隔离，不能从潜客结果直接生成正式知识资产。
5. M25R 已完成 50 家补证、report-only/gate 和可信复核；真实写回仍需单独确认。
