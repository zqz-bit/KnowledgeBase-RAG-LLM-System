# KnowledgeBase-RAG-LLM-System

 ## 项目测试记录
---

## ✨ 测试内容

### 第1次测试：Parent-Child Chunking 全链路对照评测

#### 测试目的
本次测试用于验证第1次更新引入的 Parent-Child Chunking 是否真的适合当前项目的知识复用场景，尤其关注用户阅读小林 coding、技术文档、课程资料后，再通过 RAG 复习时，回答是否能更好地复用原文知识结构、术语、分类和因果链。

本次测试不只观察检索是否命中，也观察命中后交给大模型的上下文是否更干净、回答是否更贴近资料原有讲法，以及整体延迟和上下文成本是否可接受。

#### 测试方案
本次采用 A/B 对照方式测试两种入库与检索策略：

- Flat 普通分块：原文直接按 1000 字符切分，重叠 100 字符，检索后直接把命中的 chunk 交给大模型回答。
- Parent-Child 父子分块：原文先切 parent 2000 字符、重叠 200 字符，再把 parent 切成 child 400 字符、重叠 80 字符；检索时命中 child，回答时回查对应 parent，把更完整的 parent 上下文交给大模型。

两组测试使用相同资料、相同问题、相同 embedding 模型、相同大模型、相同混合检索逻辑和相同自动评分标准。

#### 测试资料与配置
- 资料来源：小林 coding 公开仓库 `https://github.com/xiaolincoder/CS-Base`
- 测试案例数量：12 个正式案例
- 覆盖主题：MySQL MVCC、TCP、IP、ARP、操作系统进程、Redis、RDB、AOF
- Embedding 模型：`text-embedding-v4`
- Chat 模型：`qwen3-max`
- 检索策略：BM25 + 向量检索 + RRF 重排
- 正式测试结果文件：`benchmark_results/parent_child_benchmark_20260517_125710.md`
- 正式测试明细 JSON：`benchmark_results/parent_child_benchmark_20260517_125710.json`
- 测试脚本：`benchmarks/parent_child_benchmark.py`

#### 评测指标
- Hit Rate：检索结果是否命中标准资料章节。
- Context Coverage：检索上下文覆盖标准资料关键词的比例。
- Context Noise：检索上下文中不属于标准资料关键词的比例，越低越好。
- Answer Gold Overlap：回答内容与标准资料关键词的重合程度。
- LLM Quality：由大模型裁判基于标准资料评分，包含事实正确性、资料支撑度、关键点覆盖、结构复用四项。
- Structure Preservation：回答是否沿用原文知识结构、术语、分类和因果链。
- Avg Context Chars：平均交给大模型的上下文字符数。
- Avg Total Seconds：平均检索与回答总耗时。

#### 测试结果
| Metric | Flat | Parent-Child | Change |
| --- | ---: | ---: | ---: |
| Hit Rate | 100.00% | 91.67% | -8.33% |
| Context Coverage | 96.31% | 92.49% | -3.97% |
| Context Noise | 48.05% | 36.77% | -23.48% |
| Answer Gold Overlap | 49.18% | 48.76% | -0.86% |
| LLM Quality 0-5 | 3.896 | 4.146 | 6.42% |
| Avg Context Chars | 2394.000 | 2556.417 | 6.78% |
| Avg Total Seconds | 21.901 | 21.988 | 0.40% |

#### 知识复用结果
- 综合回答质量提升：6.42%
- 原文结构复用提升：11.63%
- 上下文噪声降低：23.48%
- 上下文字符数增加：6.78%
- 总延迟增加：0.40%
- 单位上下文质量效率变化：-0.34%

#### 测试结论
本次测试说明，Parent-Child Chunking 并不保证检索命中率一定提升。本次 12 个案例中，父子分块有 1 个短泛问题“进程”没有命中标准章节，导致 Hit Rate 从 100.00% 降到 91.67%。

但父子分块在命中后的上下文质量上表现更好：Context Noise 从 48.05% 降到 36.77%，说明交给大模型的资料更干净；LLM Quality 从 3.896 提升到 4.146，说明回答质量更好；Structure Preservation 从 3.583 提升到 4.000，说明回答更容易复用原文的知识结构、术语、分类和因果链。

因此，本次测试结论是：Parent-Child Chunking 更适合作为回答质量和知识结构复用优化方案，而不是单独的召回率优化方案。对于当前项目“知识复用、降低重复记忆成本”的目标，父子分块值得保留；后续如果要提升短泛问题的命中率，应继续增加标题增强、Query Rewrite、多查询扩展或 parent 级补召回。

#### 测试过程补充
正式测试前先运行了 3 个案例的小样本冒烟测试，确认脚本可以完成独立临时索引构建、检索、回答、结果落盘。该小样本只用于验证测试流程，不作为正式结论。

正式测试过程中发现并处理了 DashScope embedding 单批最多 10 条文本的限制，测试脚本已改为分批写入 Chroma，避免批量过大导致入库失败。

测试过程中 Chroma 输出过 telemetry 警告，例如 `Failed to send telemetry event...`，但不影响索引构建、检索、模型回答和结果生成。

### 第2次测试：BM25 + 向量检索 + RRF 重排对照评测

#### 测试目的
本次测试用于验证第4次更新引入的 BM25 + 向量检索 + RRF 重排是否相比单路向量检索有实际提升。测试重点是检索策略本身，因此本次固定使用同一套 Parent-Child Chunking，只切换 child 阶段的检索方式。

本次测试关注精确术语、英文缩写、协议字段、语义改写等问题，观察混合检索是否能提升命中率、排序质量、关键术语召回、回答质量，以及是否带来额外上下文噪声和耗时。

#### 测试方案
本次采用 A/B 对照方式测试两种检索策略：

- Vector Only：只使用 child 向量检索 Top6，再取 Top3 child 回查 parent。
- Hybrid RRF：使用 child 向量检索 Top6 + child BM25 检索 Top6，再通过 RRF 融合重排取 Top3 child 回查 parent。

两组测试使用相同资料、相同问题、相同 parent-child 分块、相同 embedding 模型、相同大模型、相同 parent 回查逻辑和相同自动评分标准。

#### 测试资料与配置
- 资料来源：小林 coding 公开仓库 `https://github.com/xiaolincoder/CS-Base`
- 测试案例数量：20 个正式案例
- 测试问题类型：精确术语、英文/中文混合关键词、协议字段、语义改写
- 原始资料文件数量：12 个 Markdown 文件
- 过滤后的原文区域：115 个章节 section
- Parent chunk 数量：134 个
- Child 向量 chunk 数量：536 个
- Embedding 模型：`text-embedding-v4`
- Chat 模型：`qwen3-max`
- 正式测试结果文件：`benchmark_results/hybrid_retrieval_benchmark_20260517_160531.md`
- 正式测试明细 JSON：`benchmark_results/hybrid_retrieval_benchmark_20260517_160531.json`
- 测试脚本：`benchmarks/hybrid_retrieval_benchmark.py`

#### 评测指标
- Hit Rate：最终 Top3 parent 是否包含标准章节。
- MRR：标准章节第一次出现的排名倒数，越高越好。
- Exact Term Recall：问题中的关键术语、英文缩写、协议字段是否出现在检索上下文中。
- Context Coverage：检索上下文覆盖标准资料关键词的比例。
- Context Noise：检索上下文中不属于标准资料关键词的比例，越低越好。
- Answer Gold Overlap：回答内容与标准资料关键词的重合程度。
- LLM Quality：由大模型裁判基于标准资料评分，包含事实正确性、资料支撑度、关键点覆盖、术语保留、结构复用五项。
- Avg Retrieval Seconds：平均检索耗时。
- Avg Total Seconds：平均检索与回答总耗时。

#### 测试结果
| Metric | Vector Only | Hybrid RRF | Change |
| --- | ---: | ---: | ---: |
| Hit Rate | 100.00% | 100.00% | 0.00% |
| MRR | 0.975 | 0.975 | 0.00% |
| Exact Term Recall | 100.00% | 100.00% | 0.00% |
| Context Coverage | 98.23% | 96.63% | -1.63% |
| Context Noise | 21.84% | 23.96% | 9.69% |
| Answer Gold Overlap | 39.37% | 38.80% | -1.46% |
| LLM Quality 0-5 | 4.560 | 4.660 | 2.19% |
| Avg Context Chars | 2462.300 | 2553.650 | 3.71% |
| Avg Retrieval Seconds | 0.453 | 0.390 | -13.99% |
| Avg Total Seconds | 20.879 | 20.503 | -1.80% |

#### 分类结果
| Category | Cases | Vector Hit | Hybrid Hit | Vector MRR | Hybrid MRR | Vector Term Recall | Hybrid Term Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exact_term | 5 | 100.00% | 100.00% | 1.000 | 1.000 | 100.00% | 100.00% |
| mixed_keyword | 5 | 100.00% | 100.00% | 1.000 | 1.000 | 100.00% | 100.00% |
| protocol_field | 5 | 100.00% | 100.00% | 1.000 | 1.000 | 100.00% | 100.00% |
| semantic | 5 | 100.00% | 100.00% | 0.900 | 0.900 | 100.00% | 100.00% |

#### 知识复用结果
- 检索命中率变化：0.00%
- MRR 排序质量变化：0.00%
- 关键术语召回变化：0.00%
- 综合回答质量提升：2.19%
- 上下文噪声增加：9.69%
- 上下文字符数增加：3.71%
- 检索耗时变化：-13.99%
- 总耗时变化：-1.80%
- 自动裁判结果：Vector Only 赢 4 题，Hybrid RRF 赢 5 题，平局 11 题。

#### 测试结论
本次测试中，Vector Only 已经表现很强，20 个问题全部命中标准章节，Exact Term Recall 也已经达到 100%。因此，Hybrid RRF 在命中率、MRR 和关键术语召回上没有体现出额外提升。

Hybrid RRF 的主要收益体现在回答质量上：LLM Quality 从 4.560 提升到 4.660，提升 2.19%；自动裁判中 Hybrid RRF 赢 5 题，Vector Only 赢 4 题，平局 11 题，说明混合检索在部分问题上能改善最终回答，但整体提升幅度不大。

需要注意的是，Hybrid RRF 的 Context Noise 从 21.84% 增加到 23.96%，说明 BM25 引入的关键词命中有时会带来额外相关但非标准章节的上下文。平均检索耗时和总耗时本次略低，但模型 API 波动会影响该指标，不能简单理解为混合检索一定更快。

因此，本次测试结论是：BM25 + 向量检索 + RRF 重排值得保留，尤其适合作为精确术语和关键词召回的兜底机制；但在当前小林 coding 测试集上，单路向量检索已经足够强，混合检索的边际收益较小。后续如果要进一步放大 BM25 的价值，应测试更多编号、课程代码、配置项、函数名、报错信息、文件名等强关键词场景，并考虑给 BM25 文档加入标题和章节路径权重。

#### 测试过程补充
正式测试前先运行了 3 个案例的小样本冒烟测试，确认脚本可以完成临时索引构建、两种检索模式切换、模型回答和结果落盘。该小样本只用于验证流程，不作为正式结论。

测试过程中 Chroma 仍输出 telemetry 警告，例如 `Failed to send telemetry event...`，但不影响索引构建、检索、模型回答和结果生成。

### 第3次测试：强标识符文档下的混合检索对照评测

#### 测试目的
第2次测试仍使用小林 coding 的自然语言技术文章，Vector Only 已经能很好命中标准章节，因此 BM25 + RRF 的差异不明显。本次测试改用更适合混合检索发挥作用的强标识符文档，重点验证 BM25 对命令名、字段名、camelCase 配置项、英文缩写等精确匹配场景的提升。

本次测试关注：当问题包含 `HEXPIRE`、`FUNCTION LIST`、`terminationGracePeriodSeconds`、`fsGroupChangePolicy` 等精确标识符时，Hybrid RRF 是否比单路向量检索更容易命中正确资料。

#### 测试方案
本次采用 A/B 对照方式测试两种检索策略：

- Vector Only：只使用向量检索 Top6，再取 Top3 作为上下文。
- Hybrid RRF：使用向量检索 Top6 + BM25 检索 Top6，再通过 RRF 融合重排取 Top3 作为上下文。

两组测试使用相同资料、相同问题、相同 embedding 模型、相同大模型、相同自动评分标准。不同于前两次测试，本次语料以独立短文档为单位，每个 Redis 命令或 Kubernetes 字段都是一个可检索 section。

#### 测试资料与配置
- Redis 命令资料来源：`https://github.com/redis/redis/tree/unstable/src/commands`
- Kubernetes API 资料来源：`https://github.com/kubernetes/api`
- 测试案例数量：20 个正式案例
- 测试问题类型：Redis 命令、Kubernetes API 字段
- 强标识符 section 数量：1699 个
- Redis 命令问题数量：10 个
- Kubernetes 字段问题数量：10 个
- Embedding 模型：`text-embedding-v4`
- Chat 模型：`qwen3-max`
- 正式测试结果文件：`benchmark_results/identifier_hybrid_benchmark_20260517_170026.md`
- 正式测试明细 JSON：`benchmark_results/identifier_hybrid_benchmark_20260517_170026.json`
- 测试脚本：`benchmarks/identifier_hybrid_benchmark.py`

#### 评测指标
- Hit Rate：最终 Top3 是否包含标准标识符文档。
- MRR：标准文档第一次出现的排名倒数，越高越好。
- Identifier@1：Top1 是否就是标准标识符文档。
- Exact Term Recall：问题中的命令名、字段名等精确术语是否出现在检索上下文中。
- Context Coverage：检索上下文覆盖标准资料关键词的比例。
- Context Noise：检索上下文中不属于标准资料关键词的比例，越低越好。
- Answer Gold Overlap：回答内容与标准资料关键词的重合程度。
- LLM Quality：由大模型裁判基于标准资料评分，包含事实正确性、资料支撑度、关键点覆盖、标识符保留四项。
- Avg Retrieval Seconds：平均检索耗时。
- Avg Total Seconds：平均检索与回答总耗时。

#### 测试结果
| Metric | Vector Only | Hybrid RRF | Change |
| --- | ---: | ---: | ---: |
| Hit Rate | 50.00% | 75.00% | 50.00% |
| MRR | 0.475 | 0.650 | 36.84% |
| Identifier@1 | 45.00% | 60.00% | 33.33% |
| Exact Term Recall | 72.50% | 85.00% | 17.24% |
| Context Coverage | 71.11% | 86.37% | 21.45% |
| Context Noise | 44.15% | 37.25% | -15.65% |
| Answer Gold Overlap | 7.31% | 12.12% | 65.84% |
| LLM Quality 0-5 | 2.325 | 3.337 | 43.55% |
| Avg Context Chars | 2160.100 | 2156.200 | -0.18% |
| Avg Retrieval Seconds | 0.823 | 0.631 | -23.35% |
| Avg Total Seconds | 3.203 | 3.761 | 17.43% |

#### 分类结果
| Category | Cases | Vector Hit | Hybrid Hit | Vector MRR | Hybrid MRR | Vector @1 | Hybrid @1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| redis_command | 10 | 80.00% | 90.00% | 0.800 | 0.900 | 80.00% | 90.00% |
| k8s_field | 10 | 20.00% | 60.00% | 0.150 | 0.400 | 10.00% | 30.00% |

#### 知识复用结果
- 检索命中率提升：50.00%
- MRR 排序质量提升：36.84%
- Top1 标识符命中提升：33.33%
- 精确术语召回提升：17.24%
- 上下文覆盖度提升：21.45%
- 上下文噪声降低：15.65%
- 综合回答质量提升：43.55%
- 平均上下文字符数基本持平：-0.18%
- 平均检索耗时变化：-23.35%
- 平均总耗时增加：17.43%
- 自动裁判结果：Vector Only 赢 3 题，Hybrid RRF 赢 8 题，平局 9 题。

#### 测试结论
本次测试能明显体现 BM25 + 向量检索 + RRF 的价值。相比 Vector Only，Hybrid RRF 的 Hit Rate 从 50.00% 提升到 75.00%，MRR 从 0.475 提升到 0.650，LLM Quality 从 2.325 提升到 3.337。

提升最明显的是 Kubernetes API 字段类问题：Vector Only 只命中 20.00%，Hybrid RRF 命中 60.00%。例如 `PodSpec.terminationGracePeriodSeconds`、`PodSpec.hostUsers`、`JobSpec.podReplacementPolicy` 这类 camelCase 字段，向量检索容易被语义相近字段干扰，而 BM25 能直接利用精确字段名把正确文档拉回来。

Redis 命令类问题中，Hybrid RRF 也有小幅提升：命中率从 80.00% 提升到 90.00%。典型例子是 `FUNCTION LIST`，Vector Only 命中的是 `FUNCTION` 和 `FUNCTION HELP`，Hybrid RRF 能命中准确的 `FUNCTION LIST` 文档。

因此，本次测试结论是：在自然语言知识文章里，混合检索的边际收益可能不明显；但在命令、配置项、字段名、函数名、错误码、课程代码、文件名等强标识符场景下，BM25 + 向量检索 + RRF 能显著提升检索命中率、排序质量和最终回答质量，应该作为项目的长期默认检索策略保留。

#### 测试过程补充
正式测试前先运行了 3 个 Redis 命令案例的小样本冒烟测试，确认脚本可以完成强标识符语料构建、临时索引构建、两种检索模式切换、模型回答和结果落盘。该小样本只用于验证流程，不作为正式结论。

测试过程中 Chroma 仍输出 telemetry 警告，例如 `Failed to send telemetry event...`，但不影响索引构建、检索、模型回答和结果生成。

### 第4次测试：Qwen 结合上下文进行 Query Rewrite 全链路评测

#### 测试目的
本次测试用于验证项目中“用 Qwen 结合最近对话历史改写用户查询”的功能是否真的能提升最终回答质量。测试重点是多轮问答里的指代、省略和对比问题，例如用户先说“我在复习 AOF 后台重写”，随后问“那新写入的命令怎么处理？”。

本次不测试上下文压缩；测试历史中只放最近一轮用户与助手消息，不放长期摘要。

#### 测试方案
本次采用 A/B 对照方式测试两条完整链路：

- Original Query：直接使用用户当前问题检索，然后基于检索上下文生成回答。
- Rewritten Query：先把最近历史和当前问题发给项目里的 `QueryRewriteService`，由 Qwen 改写成清晰问题，再用改写后的问题检索并生成回答。

两组测试使用相同资料、相同 Parent-Child Chunking、相同 BM25 + 向量检索 + RRF 重排、相同 embedding 模型和相同回答模型，只切换是否经过 Qwen 查询改写。回答生成后，再让 Qwen 根据标准资料对两边回答打分。

#### 测试资料与配置
- 资料来源：小林 coding 公开仓库 `https://github.com/xiaolincoder/CS-Base`
- 测试案例数量：20 个正式案例
- 测试问题类型：指代问题、省略问题、对比问题
- 覆盖主题：TCP、HTTP、ARP、CIDR、MySQL MVCC、Redis、操作系统进程、虚拟内存、I/O 多路复用
- Chat 模型：`qwen3-max`
- Rewrite 模型：`qwen3-max`
- Embedding 模型：`text-embedding-v4`
- 检索策略：Parent-Child Chunking + BM25 + 向量检索 + RRF 重排
- 正式测试结果文件：`benchmark_results/query_rewrite_benchmark_20260517_200251.md`
- 正式测试明细 JSON：`benchmark_results/query_rewrite_benchmark_20260517_200251.json`
- 测试脚本：`benchmarks/query_rewrite_benchmark.py`

#### 评测指标
- Query Term Recall：当前查询是否补全并保留标准关键术语。
- Hit Rate：最终 Top3 parent 是否包含标准资料章节。
- MRR：标准章节第一次出现的排名倒数，越高说明正确资料排得越靠前。
- Context Coverage：检索上下文覆盖标准资料关键词的比例。
- Context Noise：检索上下文中不属于标准资料关键词的比例，越低越好。
- Answer Gold Overlap：回答内容与标准资料关键词的重合程度。
- LLM Quality：由大模型裁判基于标准资料评分，包含事实正确性、资料支撑度、关键点覆盖、术语保留、结构复用五项。
- Avg Retrieval+Answer Seconds：平均检索与回答耗时，不包含 Qwen 改写耗时。
- Avg End-to-End Seconds：端到端平均耗时；改写链路包含 Qwen 改写、检索和回答。

#### 测试结果
| Metric | Original Query | Rewritten Query | Change |
| --- | ---: | ---: | ---: |
| Query Term Recall | 24.17% | 98.33% | 306.90% |
| Hit Rate | 55.00% | 100.00% | 81.82% |
| MRR | 0.458 | 0.875 | 90.91% |
| Context Coverage | 68.01% | 98.63% | 45.02% |
| Context Noise | 55.58% | 26.85% | -51.68% |
| Answer Gold Overlap | 25.98% | 30.80% | 18.53% |
| LLM Quality 0-5 | 3.890 | 4.840 | 24.42% |
| Avg Context Chars | 3743.850 | 2944.200 | -21.36% |
| Avg Retrieval Seconds | 0.218 | 0.318 | 45.82% |
| Avg Retrieval+Answer Seconds | 11.334 | 11.482 | 1.31% |
| Avg End-to-End Seconds | 11.334 | 12.703 | 12.08% |

#### 分类结果
| Category | Cases | Original Hit | Rewritten Hit | Original Term Recall | Rewritten Term Recall | Original Quality | Rewritten Quality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| comparison | 3 | 0.00% | 100.00% | 0.00% | 100.00% | 2.067 | 4.867 |
| ellipsis | 8 | 62.50% | 100.00% | 33.33% | 100.00% | 3.825 | 4.725 |
| pronoun | 9 | 66.67% | 100.00% | 24.07% | 96.30% | 4.556 | 4.933 |

#### 知识复用结果
- 查询关键术语召回提升：306.90%
- 检索命中率提升：81.82%
- MRR 排序质量提升：90.91%
- 上下文覆盖度提升：45.02%
- 上下文噪声降低：51.68%
- 回答关键词重合提升：18.53%
- 综合回答质量提升：24.42%
- 平均上下文字符数降低：21.36%
- 由 Query Rewrite 修复的未命中案例：9 个
- Query Rewrite 造成的回退案例：0 个
- 自动裁判结果：Original Query 赢 2 题，Rewritten Query 赢 10 题，平局 8 题。
- Qwen 平均改写耗时：1.221 秒
- 平均端到端耗时增加：12.08%，从 11.334 秒增加到 12.703 秒

#### 测试结论
本次全链路测试说明，Qwen 结合上下文进行 Query Rewrite 不只是让检索更准，也能明显提升最终回答质量。LLM Quality 从 3.890 提升到 4.840，提升 24.42%；自动裁判中改写链路赢 10 题，原始链路赢 2 题，平局 8 题。

提升最明显的是对比类问题。原始问题只问“它俩主要差别是什么？”、“它比前两个改进了什么？”时，直接检索完全无法命中标准章节；结合历史改写后能补出 “LRU/LFU”“epoll/select/poll” 等关键主题，因此对比类回答质量从 2.067 提升到 4.867。

代价主要是延迟：每次请求会增加一次 Qwen 改写调用，本次平均改写耗时 1.221 秒；端到端耗时从 11.334 秒增加到 12.703 秒，增加 12.08%。对于当前项目“知识复用、降低重复记忆成本”的目标，Query Rewrite 的质量收益明显大于延迟成本，建议继续作为默认链路保留。

#### 测试过程补充
正式测试前先运行了 2 个案例的小样本冒烟测试，确认项目的 `QueryRewriteService` 可以正常调用 Qwen，并且回答生成、Qwen 裁判和 JSON 解析都可以跑通。冒烟测试只用于验证流程，不作为正式结论。

本次最终报告在上一次纯检索 Query Rewrite 测试基础上新增了 `Answer Gold Overlap` 和 `LLM Quality 0-5`，因此结论以 `query_rewrite_benchmark_20260517_200251` 这份全链路报告为准。

测试过程中 Chroma 仍输出 telemetry 警告，例如 `Failed to send telemetry event...`，但不影响索引构建、检索、Qwen 改写、模型回答、裁判评分和结果生成。
