# Identifier Hybrid Retrieval Benchmark

- Redis source: https://github.com/redis/redis/tree/unstable/src/commands
- Kubernetes API source: https://github.com/kubernetes/api
- Cases: 3
- Sections: 1699
- Chat model: qwen3-max
- Embedding model: text-embedding-v4

## Summary

| Metric | Vector Only | Hybrid RRF | Change |
| --- | ---: | ---: | ---: |
| Hit Rate | 100.00% | 100.00% | 0.00% |
| MRR | 1.000 | 1.000 | 0.00% |
| Identifier@1 | 100.00% | 100.00% | 0.00% |
| Exact Term Recall | 100.00% | 100.00% | 0.00% |
| Context Coverage | 100.00% | 100.00% | 0.00% |
| Context Noise | 29.59% | 29.14% | -1.54% |
| Answer Gold Overlap | 10.46% | 10.76% | 2.83% |
| LLM Quality 0-5 | 0.000 | 0.000 | N/A |
| Avg Context Chars | 3166.333 | 2767.000 | -12.61% |
| Avg Retrieval Seconds | 1.174 | 0.532 | -54.68% |
| Avg Total Seconds | 5.881 | 4.981 | -15.31% |

## Category Summary

| Category | Cases | Vector Hit | Hybrid Hit | Vector MRR | Hybrid MRR | Vector @1 | Hybrid @1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| redis_command | 3 | 100.00% | 100.00% | 1.000 | 1.000 | 100.00% | 100.00% |

## Winners

- Vector Only: 0
- Hybrid RRF: 0
- Tie: 0

## Cases

### case_01 Redis HEXPIRE

- Category: redis_command
- Question: Redis 命令 HEXPIRE 是做什么的？复杂度和返回值语义是什么？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis HEXPIRE', 'Redis HEXPIRETIME', 'Redis HEXPIREAT']
- Hybrid retrieved: ['Redis HEXPIRE', 'Redis HEXPIRETIME', 'Redis LOLWUT']
- Judge: `{}`

### case_02 Redis HPEXPIRETIME

- Category: redis_command
- Question: Redis 命令 HPEXPIRETIME 返回什么？和 hash field expiration 有什么关系？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis HPEXPIRETIME', 'Redis HPEXPIREAT', 'Redis HPEXPIRE']
- Hybrid retrieved: ['Redis HPEXPIRETIME', 'Redis HEXPIRETIME', 'Redis HPEXPIRE']
- Judge: `{}`

### case_03 Redis HPERSIST

- Category: redis_command
- Question: Redis 命令 HPERSIST 的作用是什么？它对 hash field 的过期时间做什么？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis HPERSIST', 'Redis PERSIST', 'Redis LASTSAVE']
- Hybrid retrieved: ['Redis HPERSIST', 'Redis PERSIST', 'Redis HEXISTS']
- Judge: `{}`
