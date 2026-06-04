# Parent-Child Chunking Benchmark

- Source: https://github.com/xiaolincoder/CS-Base
- Cases: 3
- Chat model: qwen3-max
- Embedding model: text-embedding-v4

## Summary

| Metric | Flat | Parent-Child | Change |
| --- | ---: | ---: | ---: |
| Hit Rate | 100.00% | 100.00% | 0.00% |
| Context Coverage | 93.95% | 97.33% | 3.59% |
| Context Noise | 37.51% | 12.33% | -67.14% |
| Answer Gold Overlap | 41.58% | 43.94% | 5.68% |
| LLM Quality 0-5 | N/A | N/A | N/A |
| Avg Context Chars | 2586.667 | 2256.667 | -12.76% |
| Avg Total Seconds | 19.957 | 19.875 | -0.41% |

## Knowledge Reuse

- Quality relative improvement: N/A
- Structure preservation relative improvement: N/A
- Context chars relative change: -12.76%
- Latency relative change: -0.41%
- Quality per 1k context chars change: N/A

## Cases

### case_01 调度原则

- Question: 资料中是如何解释「调度原则」的？请尽量保留原文的术语、层次和因果链。
- Gold source: os/4_process/process_base.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{}`

### case_02 Redis 使用的过期删除策略是什么？

- Question: 面试复习时如果被问到「Redis 使用的过期删除策略是什么？」，应该按照资料里的讲法怎么回答？
- Gold source: redis/base/redis_interview.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{}`

### case_03 AOF 后台重写

- Question: 我想按资料原文的知识结构复习「AOF 后台重写」，请说明核心机制、分类和关键原因。
- Gold source: redis/storage/aof.md
- Flat hit: True; Parent-Child hit: True
- Judge: `{}`
