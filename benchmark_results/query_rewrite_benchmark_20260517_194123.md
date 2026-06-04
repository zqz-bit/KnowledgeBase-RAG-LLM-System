# Query Rewrite Benchmark

- Source: https://github.com/xiaolincoder/CS-Base
- Cases: 20
- Rewrite model: qwen3-max
- Embedding model: text-embedding-v4
- Retrieval: parent-child + hybrid RRF

## Summary

| Metric | Original Query | Rewritten Query | Change |
| --- | ---: | ---: | ---: |
| Query Term Recall | 24.17% | 100.00% | 313.79% |
| Hit Rate | 50.00% | 95.00% | 90.00% |
| MRR | 0.408 | 0.825 | 102.04% |
| Context Coverage | 66.60% | 95.96% | 44.09% |
| Context Noise | 59.49% | 31.02% | -47.85% |
| Avg Context Chars | 3821.750 | 2946.000 | -22.91% |
| Avg Retrieval Seconds | 0.196 | 0.381 | 94.65% |

## Rewrite Stats

- Rewrite changed rate: 100.00%
- Avg rewrite seconds: 1.286
- Fixed misses: 9
- Regressions: 0

## Category Summary

| Category | Cases | Original Hit | Rewritten Hit | Original Term Recall | Rewritten Term Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| comparison | 3 | 0.00% | 100.00% | 0.00% | 100.00% |
| ellipsis | 8 | 62.50% | 100.00% | 33.33% | 100.00% |
| pronoun | 9 | 55.56% | 88.89% | 24.07% | 100.00% |

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
- Rewritten query: 为什么 TIME_WAIT 状态要等待 2MSL 这么久？
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
- Original retrieved: ['如何避免缓存雪崩、缓存击穿、缓存穿透？', 'TCP 和 UDP 可以使用同一个端口吗？']
- Rewritten retrieved: ['什么是 SYN 攻击？如何避免 SYN 攻击？']

### case_04 TCP 四次挥手过程是怎样的？

- Category: ellipsis
- History: user: 我正在复习「TCP 四次挥手过程是怎样的？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「TCP 四次挥手过程是怎样的？」。后续问题我会围绕这个主题理解。
- Original query: FIN 和 ACK 是怎么交互的？
- Rewritten query: 在 TCP 四次挥手过程中，FIN 和 ACK 报文是如何交互的？
- Original hit/rank: True / 3
- Rewritten hit/rank: True / 3
- Original retrieved: ['第三次挥手丢失了，会发生什么？', '第一次挥手丢失了，会发生什么？', 'TCP 四次挥手过程是怎样的？']
- Rewritten retrieved: ['第四次挥手丢失了，会发生什么？', '第一次挥手丢失了，会发生什么？', 'TCP 四次挥手过程是怎样的？']

### case_05 HTTP/2 做了什么优化？

- Category: pronoun
- History: user: 我正在复习「HTTP/2 做了什么优化？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「HTTP/2 做了什么优化？」。后续问题我会围绕这个主题理解。
- Original query: 它的头部压缩和 Stream 是怎么优化的？
- Rewritten query: HTTP/2 的头部压缩和 Stream 机制是如何实现性能优化的？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['HTTP/2 做了什么优化？']
- Rewritten retrieved: ['HTTP/2 做了什么优化？']

### case_06 HTTP/3 做了哪些优化？

- Category: pronoun
- History: user: 我正在复习「HTTP/3 做了哪些优化？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「HTTP/3 做了哪些优化？」。后续问题我会围绕这个主题理解。
- Original query: 它和 QUIC 解决了哪些问题？
- Rewritten query: HTTP/3 和 QUIC 解决了哪些问题？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['HTTP/3 做了哪些优化？']
- Rewritten retrieved: ['HTTP/3 做了哪些优化？']

### case_07 ARP

- Category: ellipsis
- History: user: 我正在复习「ARP」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「ARP」。后续问题我会围绕这个主题理解。
- Original query: 它是怎么根据 IP 地址找到 MAC 地址的？
- Rewritten query: ARP 是如何根据 IP 地址找到对应的 MAC 地址的？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['ARP']
- Rewritten retrieved: ['ARP']

### case_08 无分类地址 CIDR

- Category: ellipsis
- History: user: 我正在复习「无分类地址 CIDR」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「无分类地址 CIDR」。后续问题我会围绕这个主题理解。
- Original query: 这个斜杠后面的数字是什么意思？
- Rewritten query: 在无分类地址 CIDR 中，斜杠后面的数字是什么意思？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['无分类地址 CIDR', 'AOF 日志是如何实现的？', 'HTTP/2 做了什么优化？']
- Rewritten retrieved: ['无分类地址 CIDR', 'IP 地址的分类']

### case_09 Read View 在 MVCC 里如何工作的？

- Category: pronoun
- History: user: 我正在复习「Read View 在 MVCC 里如何工作的？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「Read View 在 MVCC 里如何工作的？」。后续问题我会围绕这个主题理解。
- Original query: 它怎么判断版本是否可见？
- Rewritten query: Read View 在 MVCC 中如何判断一个版本是否可见？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['Read View 在 MVCC 里如何工作的？', '可重复读是如何工作的？']
- Rewritten retrieved: ['Read View 在 MVCC 里如何工作的？', '读提交是如何工作的？']

### case_10 可重复读是如何工作的？

- Category: ellipsis
- History: user: 我正在复习「可重复读是如何工作的？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「可重复读是如何工作的？」。后续问题我会围绕这个主题理解。
- Original query: 这个隔离级别是怎么做到重复读的？
- Rewritten query: 可重复读隔离级别是如何实现重复读的？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 3
- Original retrieved: ['事务的隔离级别有哪些？', '事务的隔离级别有哪些？']
- Rewritten retrieved: ['事务的隔离级别有哪些？', '事务的隔离级别有哪些？', '可重复读是如何工作的？']

### case_11 Redis 使用的过期删除策略是什么？

- Category: pronoun
- History: user: 我正在复习「Redis 使用的过期删除策略是什么？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「Redis 使用的过期删除策略是什么？」。后续问题我会围绕这个主题理解。
- Original query: 它具体用了哪几种删除策略？
- Rewritten query: Redis 具体使用了哪几种过期删除策略？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['Redis 使用的过期删除策略是什么？']
- Rewritten retrieved: ['Redis 使用的过期删除策略是什么？']

### case_12 RDB 快照是如何实现的呢？

- Category: ellipsis
- History: user: 我正在复习「RDB 快照是如何实现的呢？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「RDB 快照是如何实现的呢？」。后续问题我会围绕这个主题理解。
- Original query: fork 之后数据被修改怎么办？
- Rewritten query: 在 RDB 快照实现中，fork 之后如果数据被修改了会怎样？
- Original hit/rank: True / 2
- Rewritten hit/rank: True / 1
- Original retrieved: ['AOF 后台重写', 'RDB 快照是如何实现的呢？']
- Rewritten retrieved: ['RDB 快照是如何实现的呢？']

### case_13 AOF 后台重写

- Category: pronoun
- History: user: 我正在复习「AOF 后台重写」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「AOF 后台重写」。后续问题我会围绕这个主题理解。
- Original query: 那新写入的命令怎么处理？
- Rewritten query: 在 AOF 后台重写过程中，新写入的命令是如何处理的？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['管道', 'AOF 日志是如何实现的？']
- Rewritten retrieved: ['AOF 后台重写', 'AOF 后台重写', 'AOF 重写机制']

### case_14 LRU 算法和 LFU 算法有什么区别？

- Category: comparison
- History: user: 我正在复习「LRU 算法和 LFU 算法有什么区别？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「LRU 算法和 LFU 算法有什么区别？」。后续问题我会围绕这个主题理解。
- Original query: 它俩主要差别是什么？
- Rewritten query: LRU 算法和 LFU 算法的主要差别是什么？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['线程与进程的比较', 'Linux 内存管理', 'HTTP/2 做了什么优化？']
- Rewritten retrieved: ['LRU 算法和 LFU 算法有什么区别？']

### case_15 如何避免缓存雪崩、缓存击穿、缓存穿透？

- Category: ellipsis
- History: user: 我正在复习「如何避免缓存雪崩、缓存击穿、缓存穿透？」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「如何避免缓存雪崩、缓存击穿、缓存穿透？」。后续问题我会围绕这个主题理解。
- Original query: 这三种问题分别怎么避免？
- Rewritten query: 缓存雪崩、缓存击穿和缓存穿透这三种问题分别该如何避免？
- Original hit/rank: True / 1
- Rewritten hit/rank: True / 1
- Original retrieved: ['如何避免缓存雪崩、缓存击穿、缓存穿透？', '三种写回策略']
- Rewritten retrieved: ['如何避免缓存雪崩、缓存击穿、缓存穿透？']

### case_16 线程与进程的比较

- Category: pronoun
- History: user: 我正在复习「线程与进程的比较」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「线程与进程的比较」。后续问题我会围绕这个主题理解。
- Original query: 它们最大的区别是什么？
- Rewritten query: 线程与进程最大的区别是什么？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 3
- Original retrieved: ['Redis 和 Memcached 有什么区别？', '管道']
- Rewritten retrieved: ['process_base', '线程的实现', '线程与进程的比较']

### case_17 进程的上下文切换

- Category: ellipsis
- History: user: 我正在复习「进程的上下文切换」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「进程的上下文切换」。后续问题我会围绕这个主题理解。
- Original query: 为什么这个操作会有成本？
- Rewritten query: 为什么进程的上下文切换这个操作会有成本？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['mvcc', 'HTTP/3 做了哪些优化？', 'Redis 事务支持回滚吗？']
- Rewritten retrieved: ['进程的上下文切换']

### case_18 虚拟内存

- Category: pronoun
- History: user: 我正在复习「虚拟内存」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「虚拟内存」。后续问题我会围绕这个主题理解。
- Original query: 它解决了什么问题？
- Rewritten query: 虚拟内存解决了什么问题？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['事务的隔离级别有哪些？', 'HTTPS 解决了 HTTP 的哪些问题？', 'LRU 算法和 LFU 算法有什么区别？']
- Rewritten retrieved: ['虚拟内存', '内存分页']

### case_19 select/poll

- Category: comparison
- History: user: 我正在复习「select/poll」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「select/poll」。后续问题我会围绕这个主题理解。
- Original query: 它们的问题在哪里？
- Rewritten query: select/poll 的问题在哪里？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 2
- Original retrieved: ['NAT', '网络接口层', 'Redis 的大 key 如何处理？']
- Rewritten retrieved: ['epoll', 'select/poll']

### case_20 epoll

- Category: comparison
- History: user: 我正在复习「epoll」这个知识点，请先记住这个主题。 / assistant: 好的，我们当前讨论的主题是「epoll」。后续问题我会围绕这个主题理解。
- Original query: 它比前两个改进了什么？
- Rewritten query: epoll 相比 select 和 poll 改进了什么？
- Original hit/rank: False / None
- Rewritten hit/rank: True / 1
- Original retrieved: ['HTTP/2 做了什么优化？', 'HTTP/1.1 的性能如何？', '如何服务更多的用户？']
- Rewritten retrieved: ['epoll', 'epoll']
