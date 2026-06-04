# Query Rewrite Benchmark

- Source: https://github.com/xiaolincoder/CS-Base
- Cases: 20
- Chat model: qwen3-max
- Rewrite model: qwen3-max
- Embedding model: text-embedding-v4
- Retrieval: parent-child + hybrid RRF

## Summary

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

## Rewrite Stats

- Rewrite changed rate: 100.00%
- Avg rewrite seconds: 1.221
- Fixed misses: 9
- Regressions: 0

## Winners

- Original Query: 2
- Rewritten Query: 10
- Tie: 8
- Unknown: 0

## Category Summary

| Category | Cases | Original Hit | Rewritten Hit | Original Term Recall | Rewritten Term Recall | Original Quality | Rewritten Quality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| comparison | 3 | 0.00% | 100.00% | 0.00% | 100.00% | 2.067 | 4.867 |
| ellipsis | 8 | 62.50% | 100.00% | 33.33% | 100.00% | 3.825 | 4.725 |
| pronoun | 9 | 66.67% | 100.00% | 24.07% | 96.30% | 4.556 | 4.933 |

## Cases

### case_01 为什么是三次握手？不是两次、四次？

- Category: pronoun
- History: user: 我正在复习「为什么是三次握手？不是两次、四次？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「为什么是三次握手？不是两次、四次？」。后续问题我会围绕这个主题理解。
- Original query: 为什么它不是两次就够了？
- Rewritten query: 为什么 TCP 建立连接不是两次握手就够了？
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
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 4}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "rewritten"}`

### case_03 什么是 SYN 攻击？如何避免 SYN 攻击？

- Category: ellipsis
- History: user: 我正在复习「什么是 SYN 攻击？如何避免 SYN 攻击？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「什么是 SYN 攻击？如何避免 SYN 攻击？」。后续问题我会围绕这个主题理解。
- Original query: 那怎么避免这个问题？
- Rewritten query: 如何避免 SYN 攻击？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['如何避免缓存雪崩、缓存击穿、缓存穿透？', 'HTTPS 一定安全可靠吗？']
- Rewritten retrieved: ['什么是 SYN 攻击？如何避免 SYN 攻击？']
- Judge: `{"original": {"correctness": 2, "groundedness": 1, "keypoint_coverage": 2, "term_preservation": 2, "structure_preservation": 1}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "rewritten"}`

### case_04 TCP 四次挥手过程是怎样的？

- Category: ellipsis
- History: user: 我正在复习「TCP 四次挥手过程是怎样的？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「TCP 四次挥手过程是怎样的？」。后续问题我会围绕这个主题理解。
- Original query: FIN 和 ACK 是怎么交互的？
- Rewritten query: 在 TCP 四次挥手过程中，FIN 和 ACK 报文是如何交互的？
- Original hit/rank: True / 3
- Rewritten hit/rank: True / 3
- Original retrieved: ['第三次挥手丢失了，会发生什么？', '第一次挥手丢失了，会发生什么？', 'TCP 四次挥手过程是怎样的？']
- Rewritten retrieved: ['第四次挥手丢失了，会发生什么？', '第一次挥手丢失了，会发生什么？', 'TCP 四次挥手过程是怎样的？']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_05 HTTP/2 做了什么优化？

- Category: pronoun
- History: user: 我正在复习「HTTP/2 做了什么优化？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「HTTP/2 做了什么优化？」。后续问题我会围绕这个主题理解。
- Original query: 它的头部压缩和 Stream 是怎么优化的？
- Rewritten query: HTTP/2 的头部压缩和 Stream 机制是如何实现性能优化的？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['HTTP/2 做了什么优化？']
- Rewritten retrieved: ['HTTP/2 做了什么优化？']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_06 HTTP/3 做了哪些优化？

- Category: pronoun
- History: user: 我正在复习「HTTP/3 做了哪些优化？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「HTTP/3 做了哪些优化？」。后续问题我会围绕这个主题理解。
- Original query: 它和 QUIC 解决了哪些问题？
- Rewritten query: HTTP/3 和 QUIC 解决了哪些问题？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['HTTP/3 做了哪些优化？']
- Rewritten retrieved: ['HTTP/3 做了哪些优化？']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_07 ARP

- Category: ellipsis
- History: user: 我正在复习「ARP」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「ARP」。后续问题我会围绕这个主题理解。
- Original query: 它是怎么根据 IP 地址找到 MAC 地址的？
- Rewritten query: ARP 是如何根据 IP 地址找到对应的 MAC 地址的？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['ARP']
- Rewritten retrieved: ['ARP']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 4, "structure_preservation": 5}, "winner": "original"}`

### case_08 无分类地址 CIDR

- Category: ellipsis
- History: user: 我正在复习「无分类地址 CIDR」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「无分类地址 CIDR」。后续问题我会围绕这个主题理解。
- Original query: 这个斜杠后面的数字是什么意思？
- Rewritten query: 在无分类地址 CIDR 中，斜杠后面的数字是什么意思？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['无分类地址 CIDR', 'AOF 日志是如何实现的？', 'HTTP/2 做了什么优化？']
- Rewritten retrieved: ['无分类地址 CIDR', 'IP 地址的分类']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "term_preservation": 5, "structure_preservation": 4}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "term_preservation": 5, "structure_preservation": 4}, "winner": "tie"}`

### case_09 Read View 在 MVCC 里如何工作的？

- Category: pronoun
- History: user: 我正在复习「Read View 在 MVCC 里如何工作的？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「Read View 在 MVCC 里如何工作的？」。后续问题我会围绕这个主题理解。
- Original query: 它怎么判断版本是否可见？
- Rewritten query: Read View 在 MVCC 中如何判断一个版本是否可见？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['Read View 在 MVCC 里如何工作的？', '可重复读是如何工作的？']
- Rewritten retrieved: ['Read View 在 MVCC 里如何工作的？', '读提交是如何工作的？']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_10 可重复读是如何工作的？

- Category: ellipsis
- History: user: 我正在复习「可重复读是如何工作的？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「可重复读是如何工作的？」。后续问题我会围绕这个主题理解。
- Original query: 这个隔离级别是怎么做到重复读的？
- Rewritten query: 可重复读隔离级别是如何实现重复读的？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 3
- Original retrieved: ['事务的隔离级别有哪些？', '事务的隔离级别有哪些？']
- Rewritten retrieved: ['事务的隔离级别有哪些？', '事务的隔离级别有哪些？', '可重复读是如何工作的？']
- Judge: `{"original": {"correctness": 3, "groundedness": 2, "keypoint_coverage": 3, "term_preservation": 4, "structure_preservation": 2}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "rewritten"}`

### case_11 Redis 使用的过期删除策略是什么？

- Category: pronoun
- History: user: 我正在复习「Redis 使用的过期删除策略是什么？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「Redis 使用的过期删除策略是什么？」。后续问题我会围绕这个主题理解。
- Original query: 它具体用了哪几种删除策略？
- Rewritten query: Redis 具体使用了哪几种过期删除策略？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['Redis 使用的过期删除策略是什么？']
- Rewritten retrieved: ['Redis 使用的过期删除策略是什么？']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "term_preservation": 4, "structure_preservation": 4}, "winner": "original"}`

### case_12 RDB 快照是如何实现的呢？

- Category: ellipsis
- History: user: 我正在复习「RDB 快照是如何实现的呢？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「RDB 快照是如何实现的呢？」。后续问题我会围绕这个主题理解。
- Original query: fork 之后数据被修改怎么办？
- Rewritten query: 在 RDB 快照实现中，执行 fork 之后如果父进程修改了数据，会如何处理？
- Original hit/rank: True / 2
- Rewritten hit/rank: True / 1
- Original retrieved: ['AOF 后台重写', 'RDB 快照是如何实现的呢？']
- Rewritten retrieved: ['RDB 快照是如何实现的呢？']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 4}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "rewritten"}`

### case_13 AOF 后台重写

- Category: pronoun
- History: user: 我正在复习「AOF 后台重写」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「AOF 后台重写」。后续问题我会围绕这个主题理解。
- Original query: 那新写入的命令怎么处理？
- Rewritten query: 在 AOF 后台重写过程中，新写入的命令是如何处理的？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['管道', 'AOF 日志是如何实现的？']
- Rewritten retrieved: ['AOF 后台重写', 'AOF 后台重写', 'AOF 重写机制']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_14 LRU 算法和 LFU 算法有什么区别？

- Category: comparison
- History: user: 我正在复习「LRU 算法和 LFU 算法有什么区别？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「LRU 算法和 LFU 算法有什么区别？」。后续问题我会围绕这个主题理解。
- Original query: 它俩主要差别是什么？
- Rewritten query: LRU 算法和 LFU 算法的主要差别是什么？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['Redis 和 Memcached 有什么区别？', 'Linux 内存管理', 'UDP 和 TCP 有什么区别呢？分别的应用场景是？']
- Rewritten retrieved: ['LRU 算法和 LFU 算法有什么区别？']
- Judge: `{"original": {"correctness": 3, "groundedness": 2, "keypoint_coverage": 2, "term_preservation": 4, "structure_preservation": 1}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "rewritten"}`

### case_15 如何避免缓存雪崩、缓存击穿、缓存穿透？

- Category: ellipsis
- History: user: 我正在复习「如何避免缓存雪崩、缓存击穿、缓存穿透？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「如何避免缓存雪崩、缓存击穿、缓存穿透？」。后续问题我会围绕这个主题理解。
- Original query: 这三种问题分别怎么避免？
- Rewritten query: 缓存雪崩、缓存击穿和缓存穿透这三种问题分别该如何避免？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['如何避免缓存雪崩、缓存击穿、缓存穿透？', '三种写回策略']
- Rewritten retrieved: ['如何避免缓存雪崩、缓存击穿、缓存穿透？']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "tie"}`

### case_16 线程与进程的比较

- Category: pronoun
- History: user: 我正在复习「线程与进程的比较」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「线程与进程的比较」。后续问题我会围绕这个主题理解。
- Original query: 它们最大的区别是什么？
- Rewritten query: 线程与进程最大的区别是什么？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 3
- Original retrieved: ['Redis 和 Memcached 有什么区别？', '管道']
- Rewritten retrieved: ['process_base', '线程的实现', '线程与进程的比较']
- Judge: `{"original": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "term_preservation": 5, "structure_preservation": 4}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "rewritten"}`

### case_17 进程的上下文切换

- Category: ellipsis
- History: user: 我正在复习「进程的上下文切换」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「进程的上下文切换」。后续问题我会围绕这个主题理解。
- Original query: 为什么这个操作会有成本？
- Rewritten query: 为什么进程的上下文切换会有成本？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['mvcc', 'HTTP/3 做了哪些优化？', 'Redis 事务支持回滚吗？']
- Rewritten retrieved: ['进程的上下文切换']
- Judge: `{"original": {"correctness": 2, "groundedness": 1, "keypoint_coverage": 2, "term_preservation": 3, "structure_preservation": 1}, "rewritten": {"correctness": 3, "groundedness": 3, "keypoint_coverage": 4, "term_preservation": 4, "structure_preservation": 3}, "winner": "rewritten"}`

### case_18 虚拟内存

- Category: pronoun
- History: user: 我正在复习「虚拟内存」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「虚拟内存」。后续问题我会围绕这个主题理解。
- Original query: 它解决了什么问题？
- Rewritten query: 虚拟内存解决了什么问题？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['事务的隔离级别有哪些？', '如何避免缓存雪崩、缓存击穿、缓存穿透？', 'LRU 算法和 LFU 算法有什么区别？']
- Rewritten retrieved: ['虚拟内存', '内存分页']
- Judge: `{"original": {"correctness": 2, "groundedness": 1, "keypoint_coverage": 2, "term_preservation": 2, "structure_preservation": 1}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "rewritten"}`

### case_19 select/poll

- Category: comparison
- History: user: 我正在复习「select/poll」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「select/poll」。后续问题我会围绕这个主题理解。
- Original query: 它们的问题在哪里？
- Rewritten query: select/poll 的问题或缺点是什么？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 2
- Original retrieved: ['NAT', '网络接口层', 'HTTP/1.1 的缺点有哪些？']
- Rewritten retrieved: ['epoll', 'select/poll']
- Judge: `{"original": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "term_preservation": 0, "structure_preservation": 0}, "rewritten": {"correctness": 4, "groundedness": 4, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "rewritten"}`

### case_20 epoll

- Category: comparison
- History: user: 我正在复习「epoll」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「epoll」。后续问题我会围绕这个主题理解。
- Original query: 它比前两个改进了什么？
- Rewritten query: epoll 相比 select 和 poll 改进了什么？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['HTTP/2 做了什么优化？', 'HTTP/1.1 的性能如何？', '如何服务更多的用户？']
- Rewritten retrieved: ['epoll', 'epoll']
- Judge: `{"original": {"correctness": 4, "groundedness": 3, "keypoint_coverage": 4, "term_preservation": 5, "structure_preservation": 3}, "rewritten": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "term_preservation": 5, "structure_preservation": 5}, "winner": "rewritten"}`
