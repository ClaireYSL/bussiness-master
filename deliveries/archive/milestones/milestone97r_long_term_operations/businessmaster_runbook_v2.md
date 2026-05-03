# BusinessMaster Runbook v2

## 标准主线

1. 学习素材接入：运行 M92R 管道，更新学习队列和知识草稿。
2. 知识资产治理：运行 M93R guard，只在来源真实且审查通过后进入正式知识资产。
3. 画像学习：运行 M94R proposal，默认不改 persona registry。
4. 潜客引擎：运行 M95R，把 `icp_reference_asset_refs` 接到 trusted pool 判断。
5. 用户输出：运行 M96R，更新工作台、索引、source trace browser。
6. 扩容：只有 readiness PASS 后，才进入 M98R 的 100-200 扩容批次。

## 禁止动作

- 不写旧 Excel。
- 不把潜客输出写入知识资产。
- 不把潜客输出写入 persona registry。
- 不把 LLM 输出作为 evidence。
- 不在静态池表达经营优先级、跟进团队、触达时间。

## 当前下一步

M98R：按阈值做规模化扩容准入，而不是盲目新增数量。
