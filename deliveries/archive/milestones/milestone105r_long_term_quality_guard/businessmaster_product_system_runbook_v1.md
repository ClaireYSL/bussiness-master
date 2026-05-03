# M105R 长期运行与质量守护

## 固定入口

- `python3 scripts/businessmaster_pipeline.py --mode readiness`
- `python3 scripts/businessmaster_pipeline.py --mode learn`
- `python3 scripts/businessmaster_pipeline.py --mode persona`
- `python3 scripts/businessmaster_pipeline.py --mode prospect`
- `python3 scripts/businessmaster_pipeline.py --mode publish`
- `python3 scripts/businessmaster_pipeline.py --mode scale-plan`

## 守护边界

- 旧 Excel 默认禁写。
- 潜客产出不得写正式知识资产。
- 潜客产出不得写 persona registry。
- 静态池不得出现动态经营字段。
- LLM 只可用于摘要、分类、草稿和缺口建议，不作为 evidence。
