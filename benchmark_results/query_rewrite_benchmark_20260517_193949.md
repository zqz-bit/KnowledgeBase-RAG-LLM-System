# Query Rewrite Benchmark

- Source: https://github.com/xiaolincoder/CS-Base
- Cases: 3
- Rewrite model: qwen3-max
- Embedding model: text-embedding-v4
- Retrieval: parent-child + hybrid RRF

## Summary

| Metric | Original Query | Rewritten Query | Change |
| --- | ---: | ---: | ---: |
| Query Term Recall | 11.11% | 100.00% | 800.00% |
| Hit Rate | 33.33% | 66.67% | 100.00% |
| MRR | 0.111 | 0.667 | 500.00% |
| Context Coverage | 56.32% | 82.14% | 45.85% |
| Context Noise | 79.01% | 48.27% | -38.91% |
| Avg Context Chars | 3990.333 | 3446.000 | -13.64% |
| Avg Retrieval Seconds | 0.191 | 0.870 | 355.39% |

## Rewrite Stats

- Rewrite changed rate: 100.00%
- Avg rewrite seconds: 1.152
- Fixed misses: 1
- Regressions: 0

## Category Summary

| Category | Cases | Original Hit | Rewritten Hit | Original Term Recall | Rewritten Term Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| ellipsis | 1 | 0.00% | 100.00% | 0.00% | 100.00% |
| pronoun | 2 | 50.00% | 50.00% | 16.67% | 100.00% |

## Cases

### case_01 TCP 三次握手过程是怎样的？

- Category: pronoun
- History: user: 我正在复习「TCP 三次握手过程是怎样的？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「TCP 三次握手过程是怎样的？」。后续问题我会围绕这个主题理解。
- Original query: 为什么它不是两次就够了？
- Rewritten query: 为什么 TCP 三次握手不能简化为两次握手？
- Original hit/rank: False / None
- Rewritten hit/rank: False / None
- Original retrieved: ['为什么是三次握手？不是两次、四次？', '为什么是三次握手？不是两次、四次？']
- Rewritten retrieved: ['为什么是三次握手？不是两次、四次？', '为什么是三次握手？不是两次、四次？']

### case_02 为什么 TIME_WAIT 等待的时间是 2MSL？

- Category: pronoun
- History: user: 我正在复习「为什么 TIME_WAIT 等待的时间是 2MSL？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「为什么 TIME_WAIT 等待的时间是 2MSL？」。后续问题我会围绕这个主题理解。
- Original query: 为什么它要等这么久？
- Rewritten query: 为什么 TIME_WAIT 状态要等待 2MSL 这么长时间？
- Original hit/rank: True / 3
- Rewritten hit/rank: True / 1
- Original retrieved: ['调度算法', 'HTTPS  是如何建立连接的？其间交互了什么？', '为什么 TIME_WAIT 等待的时间是 2MSL？']
- Rewritten retrieved: ['为什么 TIME_WAIT 等待的时间是 2MSL？', '为什么需要 TIME_WAIT 状态？']

### case_03 什么是 SYN 攻击？如何避免 SYN 攻击？

- Category: ellipsis
- History: user: 我正在复习「什么是 SYN 攻击？如何避免 SYN 攻击？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「什么是 SYN 攻击？如何避免 SYN 攻击？」。后续问题我会围绕这个主题理解。
- Original query: 那怎么避免这个问题？
- Rewritten query: 如何避免 SYN 攻击？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['如何避免缓存雪崩、缓存击穿、缓存穿透？', 'HTTPS 一定安全可靠吗？']
- Rewritten retrieved: ['什么是 SYN 攻击？如何避免 SYN 攻击？']
