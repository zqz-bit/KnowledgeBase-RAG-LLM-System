# Parent-Child Chunking Benchmark

- Source: https://github.com/xiaolincoder/CS-Base
- Cases: 12
- Chat model: qwen3-max
- Embedding model: text-embedding-v4

## Summary

| Metric | Flat | Parent-Child | Change |
| --- | ---: | ---: | ---: |
| Hit Rate | 100.00% | 91.67% | -8.33% |
| Context Coverage | 96.31% | 92.49% | -3.97% |
| Context Noise | 48.05% | 36.77% | -23.48% |
| Answer Gold Overlap | 49.18% | 48.76% | -0.86% |
| LLM Quality 0-5 | 3.896 | 4.146 | 6.42% |
| Avg Context Chars | 2394.000 | 2556.417 | 6.78% |
| Avg Total Seconds | 21.901 | 21.988 | 0.40% |

## Knowledge Reuse

- Quality relative improvement: 6.42%
- Structure preservation relative improvement: 11.63%
- Context chars relative change: 6.78%
- Latency relative change: 0.40%
- Quality per 1k context chars change: -0.34%

## Cases

### case_01 Read View 在 MVCC 里如何工作的？

- Question: 资料中是如何解释「Read View 在 MVCC 里如何工作的？」的？请尽量保留原文的术语、层次和因果链。
- Gold source: mysql/transaction/mvcc.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 5, "groundedness": 4, "keypoint_coverage": 4, "structure_preservation": 4}, "parent_child": {"correctness": 4, "groundedness": 3, "keypoint_coverage": 3, "structure_preservation": 3}, "winner": "flat"}`

### case_02 TCP 三次握手过程是怎样的？

- Question: 面试复习时如果被问到「TCP 三次握手过程是怎样的？」，应该按照资料里的讲法怎么回答？
- Gold source: network/3_tcp/tcp_interview.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 3, "groundedness": 3, "keypoint_coverage": 3, "structure_preservation": 3}, "parent_child": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 5}, "winner": "parent_child"}`

### case_03 针对 TCP 应该如何 Socket 编程？

- Question: 我想按资料原文的知识结构复习「针对 TCP 应该如何 Socket 编程？」，请说明核心机制、分类和关键原因。
- Gold source: network/3_tcp/tcp_interview.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 5}, "parent_child": {"correctness": 3, "groundedness": 3, "keypoint_coverage": 3, "structure_preservation": 3}, "winner": "flat"}`

### case_04 如何唯一确定一个 TCP 连接呢？

- Question: 资料中是如何解释「如何唯一确定一个 TCP 连接呢？」的？请尽量保留原文的术语、层次和因果链。
- Gold source: network/3_tcp/tcp_interview.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 5}, "parent_child": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_05 IP 地址的分类

- Question: 面试复习时如果被问到「IP 地址的分类」，应该按照资料里的讲法怎么回答？
- Gold source: network/4_ip/ip_base.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 4, "groundedness": 4, "keypoint_coverage": 4, "structure_preservation": 3}, "parent_child": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 5}, "winner": "parent_child"}`

### case_06 ARP

- Question: 我想按资料原文的知识结构复习「ARP」，请说明核心机制、分类和关键原因。
- Gold source: network/4_ip/ip_base.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 3, "groundedness": 3, "keypoint_coverage": 4, "structure_preservation": 3}, "parent_child": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 5}, "winner": "parent_child"}`

### case_07 调度原则

- Question: 资料中是如何解释「调度原则」的？请尽量保留原文的术语、层次和因果链。
- Gold source: os/4_process/process_base.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 5}, "parent_child": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 4}, "winner": "flat"}`

### case_08 线程与进程的比较

- Question: 面试复习时如果被问到「线程与进程的比较」，应该按照资料里的讲法怎么回答？
- Gold source: os/4_process/process_base.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 4, "groundedness": 3, "keypoint_coverage": 4, "structure_preservation": 3}, "parent_child": {"correctness": 4, "groundedness": 3, "keypoint_coverage": 4, "structure_preservation": 3}, "winner": "tie"}`

### case_09 进程

- Question: 我想按资料原文的知识结构复习「进程」，请说明核心机制、分类和关键原因。
- Gold source: os/4_process/process_base.md
- Flat hit: True; Parent-Child hit: False
- Judge: `{"flat": {"correctness": 1, "groundedness": 1, "keypoint_coverage": 2, "structure_preservation": 1}, "parent_child": {"correctness": 1, "groundedness": 1, "keypoint_coverage": 1, "structure_preservation": 1}, "winner": "flat"}`

### case_10 Redis 使用的过期删除策略是什么？

- Question: 资料中是如何解释「Redis 使用的过期删除策略是什么？」的？请尽量保留原文的术语、层次和因果链。
- Gold source: redis/base/redis_interview.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 5}, "parent_child": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_11 RDB 快照是如何实现的呢？

- Question: 面试复习时如果被问到「RDB 快照是如何实现的呢？」，应该按照资料里的讲法怎么回答？
- Gold source: redis/base/redis_interview.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 4}, "parent_child": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "structure_preservation": 5}, "winner": "parent_child"}`

### case_12 AOF 后台重写

- Question: 我想按资料原文的知识结构复习「AOF 后台重写」，请说明核心机制、分类和关键原因。
- Gold source: redis/storage/aof.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{"flat": {"correctness": 3, "groundedness": 3, "keypoint_coverage": 4, "structure_preservation": 2}, "parent_child": {"correctness": 4, "groundedness": 4, "keypoint_coverage": 5, "structure_preservation": 4}, "winner": "parent_child"}`
