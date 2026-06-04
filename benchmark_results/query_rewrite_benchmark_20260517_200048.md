# Query Rewrite Benchmark

- Source: https://github.com/xiaolincoder/CS-Base
- Cases: 2
- Chat model: qwen3-max
- Rewrite model: qwen3-max
- Embedding model: text-embedding-v4
- Retrieval: parent-child + hybrid RRF

## Summary

| Metric | Original Query | Rewritten Query | Change |
| --- | ---: | ---: | ---: |
| Query Term Recall | 16.67% | 83.33% | 400.00% |
| Hit Rate | 100.00% | 100.00% | 0.00% |
| MRR | 0.667 | 1.000 | 50.00% |
| Context Coverage | 100.00% | 100.00% | 0.00% |
| Context Noise | 35.58% | 28.60% | -19.61% |
| Answer Gold Overlap | 26.63% | 33.72% | 26.64% |
| LLM Quality 0-5 | 4.400 | 5.000 | 13.64% |
| Avg Context Chars | 4669.500 | 3977.000 | -14.83% |
| Avg Retrieval Seconds | 0.173 | 0.250 | 44.55% |
| Avg Total Seconds | 10.967 | 18.275 | 66.64% |

## Rewrite Stats

- Rewrite changed rate: 100.00%
- Avg rewrite seconds: 2.219
- Fixed misses: 0
- Regressions: 0

## Winners

- Original Query: 0
- Rewritten Query: 1
- Tie: 1
- Unknown: 0

## Category Summary

| Category | Cases | Original Hit | Rewritten Hit | Original Term Recall | Rewritten Term Recall | Original Quality | Rewritten Quality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pronoun | 2 | 100.00% | 100.00% | 16.67% | 83.33% | 4.400 | 5.000 |

## Cases

### case_01 为什么是三次握手？不是两次、四次？

- Category: pronoun
- History: user: 我正在复习「为什么是三次握手？不是两次、四次？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「为什么是三次握手？不是两次、四次？」。后续问题我会围绕这个主题理解。
- Original query: 为什么它不是两次就够了？
- Rewritten query: 为什么 TCP 建立连接时不是两次握手就够了？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['为什么是三次握手？不是两次、四次？', '为什么是三次握手？不是两次、四次？']
- Rewritten retrieved: ['为什么是三次握手？不是两次、四次？', '为什么是三次握手？不是两次、四次？']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_02 为什么 TIME_WAIT 等待的时间是 2MSL？

- Category: pronoun
- History: user: 我正在复习「为什么 TIME_WAIT 等待的时间是 2MSL？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「为什么 TIME_WAIT 等待的时间是 2MSL？」。后续问题我会围绕这个主题理解。
- Original query: 为什么它要等这么久？
- Rewritten query: 为什么 TIME_WAIT 状态要等待 2MSL 这么长时间？
- Original hit/rank: True / 3
- Rewritten hit/rank: True / 1
- Original retrieved: ['调度算法', 'HTTPS  是如何建立连接的？其间交互了什么？', '为什么 TIME_WAIT 等待的时间是 2MSL？']
- Rewritten retrieved: ['为什么 TIME_WAIT 等待的时间是 2MSL？', '为什么需要 TIME_WAIT 状态？']
- Judge: `{"original": {"correctness": 4, "groundedness": 3, "keypoint_coverage": 4, "term_preservation": 5, "structure_preservation": 3}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "rewritten"}`
