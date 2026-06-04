# Hybrid Retrieval Benchmark

- Source: https://github.com/xiaolincoder/CS-Base
- Cases: 20
- Chat model: qwen3-max
- Embedding model: text-embedding-v4
- Parent records: 134
- Child vector chunks: 536

## Summary

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

## Category Summary

| Category | Cases | Vector Hit | Hybrid Hit | Vector MRR | Hybrid MRR | Vector Term Recall | Hybrid Term Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exact_term | 5 | 100.00% | 100.00% | 1.000 | 1.000 | 100.00% | 100.00% |
| mixed_keyword | 5 | 100.00% | 100.00% | 1.000 | 1.000 | 100.00% | 100.00% |
| protocol_field | 5 | 100.00% | 100.00% | 1.000 | 1.000 | 100.00% | 100.00% |
| semantic | 5 | 100.00% | 100.00% | 0.900 | 0.900 | 100.00% | 100.00% |

## Winners

- Vector Only: 4
- Hybrid RRF: 5
- Tie: 11

## Cases

### case_01 Read View 在 MVCC 里如何工作的？

- Category: exact_term
- Question: Read View 在 MVCC 里如何工作的？请保留 Read View、活跃事务、版本链等术语。
- Gold source: mysql/transaction/mvcc.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 4, "groundedness": 4, "keypoint_coverage": 4, "term_preservation": 5, "structure_preservation": 4}, "winner": "vector_only"}`

### case_02 为什么 TIME_WAIT 等待的时间是 2MSL？

- Category: exact_term
- Question: TIME_WAIT 为什么要等待 2MSL？
- Gold source: network/3_tcp/tcp_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_03 Redis 使用的过期删除策略是什么？

- Category: exact_term
- Question: Redis 使用的过期删除策略是什么？
- Gold source: redis/base/redis_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_04 AOF 后台重写

- Category: exact_term
- Question: AOF 后台重写期间，新写入的命令是怎么处理的？
- Gold source: redis/storage/aof.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "term_preservation": 5, "structure_preservation": 4}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "hybrid_rrf"}`

### case_05 RDB 快照是如何实现的呢？

- Category: exact_term
- Question: RDB 快照是如何实现的？fork 和写时复制在其中起什么作用？
- Gold source: redis/base/redis_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 4}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 4}, "winner": "tie"}`

### case_06 select/poll

- Category: mixed_keyword
- Question: select 和 poll 的区别是什么？它们有什么性能问题？
- Gold source: os/8_network_system/selete_poll_epoll.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 3, "groundedness": 3, "keypoint_coverage": 4, "term_preservation": 4, "structure_preservation": 3}, "hybrid_rrf": {"correctness": 3, "groundedness": 3, "keypoint_coverage": 4, "term_preservation": 5, "structure_preservation": 4}, "winner": "hybrid_rrf"}`

### case_07 epoll

- Category: mixed_keyword
- Question: epoll 相比 select/poll 做了哪些改进？
- Gold source: os/8_network_system/selete_poll_epoll.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_08 HTTP/2 做了什么优化？

- Category: mixed_keyword
- Question: HTTP/2 做了什么优化？请说明 HPACK、Stream 和二进制帧。
- Gold source: network/2_http/http_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_09 HTTP/3 做了哪些优化？

- Category: mixed_keyword
- Question: HTTP/3 和 QUIC 解决了 HTTP/2 的哪些问题？
- Gold source: network/2_http/http_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_10 LRU 算法和 LFU 算法有什么区别？

- Category: mixed_keyword
- Question: Redis 里的 LRU 和 LFU 有什么区别？
- Gold source: redis/base/redis_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 4}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "hybrid_rrf"}`

### case_11 如何唯一确定一个 TCP 连接呢？

- Category: protocol_field
- Question: TCP 连接为什么可以用四元组唯一确定？四元组分别是什么？
- Gold source: network/3_tcp/tcp_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 4, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 3}, "hybrid_rrf": {"correctness": 5, "groundedness": 4, "keypoint_coverage": 4, "term_preservation": 5, "structure_preservation": 3}, "winner": "vector_only"}`

### case_12 什么是 SYN 攻击？如何避免 SYN 攻击？

- Category: protocol_field
- Question: 什么是 SYN 攻击？有哪些避免办法？
- Gold source: network/3_tcp/tcp_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_13 TCP 四次挥手过程是怎样的？

- Category: protocol_field
- Question: TCP 四次挥手里 FIN 和 ACK 是如何交互的？
- Gold source: network/3_tcp/tcp_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 3, "groundedness": 2, "keypoint_coverage": 4, "term_preservation": 5, "structure_preservation": 4}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "hybrid_rrf"}`

### case_14 ARP

- Category: protocol_field
- Question: ARP 是如何根据 IP 地址获取 MAC 地址的？
- Gold source: network/4_ip/ip_base.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_15 无分类地址 CIDR

- Category: protocol_field
- Question: CIDR 是什么？子网掩码和网络号如何理解？
- Gold source: network/4_ip/ip_base.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_16 为什么是三次握手？不是两次、四次？

- Category: semantic
- Question: 为什么建立连接不能只握手两次，也不需要四次？
- Gold source: network/3_tcp/tcp_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 4}, "winner": "vector_only"}`

### case_17 线程与进程的比较

- Category: semantic
- Question: 操作系统为什么要区分进程和线程？它们各自有什么特点？
- Gold source: os/4_process/process_base.md
- Vector hit/rank: True / 2
- Hybrid hit/rank: True / 2
- Judge: `{"vector_only": {"correctness": 3, "groundedness": 2, "keypoint_coverage": 4, "term_preservation": 4, "structure_preservation": 2}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "hybrid_rrf"}`

### case_18 进程的上下文切换

- Category: semantic
- Question: 为什么进程切换会有上下文切换成本？
- Gold source: os/4_process/process_base.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 4}, "hybrid_rrf": {"correctness": 4, "groundedness": 3, "keypoint_coverage": 4, "term_preservation": 4, "structure_preservation": 3}, "winner": "vector_only"}`

### case_19 虚拟内存

- Category: semantic
- Question: 为什么操作系统需要虚拟内存？它解决了什么问题？
- Gold source: os/3_memory/vmem.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 3, "groundedness": 2, "keypoint_coverage": 3, "term_preservation": 4, "structure_preservation": 2}, "hybrid_rrf": {"correctness": 3, "groundedness": 2, "keypoint_coverage": 3, "term_preservation": 4, "structure_preservation": 2}, "winner": "tie"}`

### case_20 如何避免缓存雪崩、缓存击穿、缓存穿透？

- Category: semantic
- Question: 缓存雪崩、缓存击穿、缓存穿透分别如何避免？
- Gold source: redis/base/redis_interview.md
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`
