# 外部LLM委派边界与最小接入说明 v1

## 1. 目的

本说明用于定义当前项目接入外部 LLM 的最小边界与最小用法。

当前接入目标不是把整个项目外包给外部模型，而是：

- 让外部 LLM 处理抽象后的结构化任务初稿
- 不发送原始知识源文件
- 不发送未经抽象的本地敏感材料

---

## 2. 允许发送的内容

允许发送给外部 LLM：

1. 本地知识库中的抽象结果
2. 主线 / 画像定义
3. 结构化字段与规则文档摘要
4. 公司名与公开资料摘要
5. 校准样本任务输入
6. 由本地整理后的中间摘要

---

## 3. 禁止发送的内容

禁止发送给外部 LLM：

1. 原始 PDF / DOCX / 内部材料全文
2. 学习知识库时使用的原始源文件
3. 本地未抽象的长文原始内容
4. 任何需要直接从本机外发的原始素材包

---

## 4. 最小接入脚本

当前最小脚本：

- [llm_delegate.py](/Users/clairaipartner/Codex/bussiness-master/scripts/llm_delegate.py)

环境变量：

- `DELEGATE_LLM_BASE_URL`
- `DELEGATE_LLM_API_KEY`
- `DELEGATE_LLM_MODEL`

脚本默认按 OpenAI 兼容接口调用：

- `POST {base_url}/chat/completions`

---

## 5. 推荐用途

优先让外部 LLM 处理：

1. 校准样本初判
2. 结构化候选分析草稿
3. 待补证点初稿
4. 对抽象输入的 JSON 化整理

不建议让外部 LLM 直接处理：

1. 原始知识源文件学习
2. 最终入池判定
3. 最终上移判定
4. 对本地未抽象长文的直接归纳

---

## 6. 校准样本最小调用示例

提示词与输入模板：

- [calibration_system.md](/Users/clairaipartner/Codex/bussiness-master/prompts/delegate/calibration_system.md)
- [calibration_user.md](/Users/clairaipartner/Codex/bussiness-master/prompts/delegate/calibration_user.md)
- [calibration_input_template.json](/Users/clairaipartner/Codex/bussiness-master/prompts/delegate/calibration_input_template.json)

示例命令：

```bash
DELEGATE_LLM_BASE_URL='https://ark.cn-beijing.volces.com/api/coding/v3' \
DELEGATE_LLM_API_KEY='***' \
DELEGATE_LLM_MODEL='ark-code-latest' \
python3 scripts/llm_delegate.py \
  --system-file prompts/delegate/calibration_system.md \
  --user-file prompts/delegate/calibration_user.md \
  --input-file prompts/delegate/calibration_input_template.json \
  --format json
```
