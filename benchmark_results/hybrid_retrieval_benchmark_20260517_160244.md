# Hybrid Retrieval Benchmark

- Source: https://github.com/xiaolincoder/CS-Base
- Cases: 3
- Chat model: qwen3-max
- Embedding model: text-embedding-v4
- Parent records: 134
- Child vector chunks: 536

## Summary

| Metric | Vector Only | Hybrid RRF | Change |
| --- | ---: | ---: | ---: |
| Hit Rate | 100.00% | 100.00% | 0.00% |
| MRR | 1.000 | 1.000 | 0.00% |
| Exact Term Recall | 100.00% | 100.00% | 0.00% |
| Context Coverage | 100.00% | 100.00% | 0.00% |
| Context Noise | 5.61% | 16.17% | 188.20% |
| Answer Gold Overlap | 45.58% | 42.27% | -7.26% |
| LLM Quality 0-5 | 0.000 | 0.000 | N/A |
| Avg Context Chars | 1603.667 | 2187.333 | 36.40% |
| Avg Retrieval Seconds | 0.923 | 0.346 | -62.54% |
| Avg Total Seconds | 18.861 | 18.129 | -3.88% |

## Category Summary

| Category | Cases | Vector Hit | Hybrid Hit | Vector MRR | Hybrid MRR | Vector Term Recall | Hybrid Term Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exact_term | 3 | 100.00% | 100.00% | 1.000 | 1.000 | 100.00% | 100.00% |

## Winners

- Vector Only: 0
- Hybrid RRF: 0
- Tie: 0

## Cases

### case_01 Read View 在 MVCC 里如何工作的？

- Category: exact_term
- Question: Read View 在 MVCC 里如何工作的？请保留 Read View、活跃事务、版本链等术语。
- Gold source: mysql/transaction/mvcc.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{}`

### case_02 为什么 TIME_WAIT 等待的时间是 2MSL？

- Category: exact_term
- Question: TIME_WAIT 为什么要等待 2MSL？
- Gold source: network/3_tcp/tcp_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{}`

### case_03 Redis 使用的过期删除策略是什么？

- Category: exact_term
- Question: Redis 使用的过期删除策略是什么？
- Gold source: redis/base/redis_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{}`
