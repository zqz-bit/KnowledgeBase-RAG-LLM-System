# Identifier Hybrid Retrieval Benchmark

- Redis source: https://github.com/redis/redis/tree/unstable/src/commands
- Kubernetes API source: https://github.com/kubernetes/api
- Cases: 20
- Sections: 1699
- Chat model: qwen3-max
- Embedding model: text-embedding-v4

## Summary

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

## Category Summary

| Category | Cases | Vector Hit | Hybrid Hit | Vector MRR | Hybrid MRR | Vector @1 | Hybrid @1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| k8s_field | 10 | 20.00% | 60.00% | 0.150 | 0.400 | 10.00% | 30.00% |
| redis_command | 10 | 80.00% | 90.00% | 0.800 | 0.900 | 80.00% | 90.00% |

## Winners

- Vector Only: 3
- Hybrid RRF: 8
- Tie: 9

## Cases

### case_01 Redis HEXPIRE

- Category: redis_command
- Question: Redis 命令 HEXPIRE 是做什么的？复杂度和返回值语义是什么？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis HEXPIRE', 'Redis HEXPIRETIME', 'Redis HEXPIREAT']
- Hybrid retrieved: ['Redis HEXPIRE', 'Redis HEXPIRETIME', 'Redis LOLWUT']
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "winner": "tie"}`

### case_02 Redis HPEXPIRETIME

- Category: redis_command
- Question: Redis 命令 HPEXPIRETIME 返回什么？和 hash field expiration 有什么关系？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis HPEXPIRETIME', 'Redis HPEXPIREAT', 'Redis HPEXPIRE']
- Hybrid retrieved: ['Redis HPEXPIRETIME', 'Redis HEXPIRETIME', 'Redis HPEXPIRE']
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "hybrid_rrf": {"correctness": 4, "groundedness": 3, "keypoint_coverage": 4, "identifier_preservation": 4}, "winner": "vector_only"}`

### case_03 Redis HPERSIST

- Category: redis_command
- Question: Redis 命令 HPERSIST 的作用是什么？它对 hash field 的过期时间做什么？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis HPERSIST', 'Redis PERSIST', 'Redis LASTSAVE']
- Hybrid retrieved: ['Redis HPERSIST', 'Redis HGET', 'Redis PERSIST']
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "identifier_preservation": 4}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "winner": "hybrid_rrf"}`

### case_04 Redis HGETDEL

- Category: redis_command
- Question: Redis 命令 HGETDEL 的语义是什么？会删除什么内容？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis HGETDEL', 'Redis HDEL', 'Redis GETDEL']
- Hybrid retrieved: ['Redis HGETDEL', 'Redis HDEL', 'Redis LOLWUT']
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "identifier_preservation": 4}, "hybrid_rrf": {"correctness": 4, "groundedness": 4, "keypoint_coverage": 5, "identifier_preservation": 5}, "winner": "hybrid_rrf"}`

### case_05 Redis XAUTOCLAIM

- Category: redis_command
- Question: Redis 命令 XAUTOCLAIM 是什么？它会如何处理 pending entries？
- Vector hit/rank: False / None
- Hybrid hit/rank: False / None
- Vector retrieved: ['Redis XINFO HELP', 'Redis XGROUP HELP', 'Redis XINFO']
- Hybrid retrieved: ['Redis XINFO HELP', 'Redis XPENDING', 'Redis XGROUP HELP']
- Judge: `{"vector_only": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "hybrid_rrf": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "winner": "tie"}`

### case_06 Redis BZMPOP

- Category: redis_command
- Question: Redis 命令 BZMPOP 的阻塞行为和返回值是什么？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis BZMPOP', 'Redis BZPOPMIN', 'Redis BZPOPMAX']
- Hybrid retrieved: ['Redis BZMPOP', 'Redis BZPOPMIN', 'Redis LOLWUT']
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "identifier_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "winner": "hybrid_rrf"}`

### case_07 Redis ZINTERCARD

- Category: redis_command
- Question: Redis 命令 ZINTERCARD 计算什么？LIMIT 参数有什么作用？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis ZINTERCARD', 'Redis ZCARD', 'Redis SINTERCARD']
- Hybrid retrieved: ['Redis ZINTERCARD', 'Redis ZCARD', 'Kubernetes LimitRangeItem.default']
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "identifier_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "identifier_preservation": 5}, "winner": "tie"}`

### case_08 Redis GEOSEARCHSTORE

- Category: redis_command
- Question: Redis 命令 GEOSEARCHSTORE 的作用是什么？它和地理空间索引有什么关系？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis GEOSEARCHSTORE', 'Redis GEOSEARCH', 'Redis GEORADIUS']
- Hybrid retrieved: ['Redis GEOSEARCHSTORE', 'Redis GEOSEARCH', 'Redis LOLWUT']
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 3, "identifier_preservation": 2}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "winner": "hybrid_rrf"}`

### case_09 Redis FUNCTION LIST

- Category: redis_command
- Question: Redis 命令 FUNCTION LIST 返回哪些 library/function 信息？
- Vector hit/rank: False / None
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis FUNCTION', 'Redis FUNCTION HELP', 'Redis LLEN']
- Hybrid retrieved: ['Redis FUNCTION LIST', 'Redis LLEN', 'Redis FUNCTION']
- Judge: `{"vector_only": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "winner": "hybrid_rrf"}`

### case_10 Redis ACL WHOAMI

- Category: redis_command
- Question: Redis 命令 ACL WHOAMI 返回什么？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Redis ACL WHOAMI', 'Redis ACL HELP', 'Redis ACL USERS']
- Hybrid retrieved: ['Redis ACL WHOAMI', 'Redis ACL', 'Redis ACL USERS']
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 3, "identifier_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 3, "identifier_preservation": 5}, "winner": "tie"}`

### case_11 Kubernetes PodSpec.terminationGracePeriodSeconds

- Category: k8s_field
- Question: Kubernetes 字段 PodSpec.terminationGracePeriodSeconds 表示什么？
- Vector hit/rank: False / None
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Kubernetes PodSpec.hostname', 'Kubernetes PodSpec.containers', 'Kubernetes PodSpec.subdomain']
- Hybrid retrieved: ['Kubernetes PodSpec.terminationGracePeriodSeconds', 'Kubernetes PodSpec.hostname', 'Kubernetes PodSpec.containers']
- Judge: `{"vector_only": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "winner": "hybrid_rrf"}`

### case_12 Kubernetes PodSpec.hostUsers

- Category: k8s_field
- Question: Kubernetes 字段 PodSpec.hostUsers 的用途是什么？
- Vector hit/rank: False / None
- Hybrid hit/rank: True / 3
- Vector retrieved: ['Kubernetes PodSpec.hostname', 'Kubernetes PodSpec.hostPID', 'Kubernetes PodSpec.hostAliases']
- Hybrid retrieved: ['Kubernetes PodSpec.hostPID', 'Kubernetes PodSpec.hostname', 'Kubernetes PodSpec.hostUsers']
- Judge: `{"vector_only": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "winner": "hybrid_rrf"}`

### case_13 Kubernetes PodSpec.runtimeClassName

- Category: k8s_field
- Question: Kubernetes 字段 PodSpec.runtimeClassName 用来选择什么？
- Vector hit/rank: True / 1
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Kubernetes PodSpec.runtimeClassName', 'Kubernetes PodSecurityContext.runAsUser', 'Kubernetes PodSpec.hostname']
- Hybrid retrieved: ['Kubernetes PodSpec.runtimeClassName', 'Kubernetes PodSpec.hostPID', 'Kubernetes PodSecurityContext.runAsUser']
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "identifier_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "identifier_preservation": 5}, "winner": "tie"}`

### case_14 Kubernetes PodSecurityContext.fsGroupChangePolicy

- Category: k8s_field
- Question: Kubernetes 字段 PodSecurityContext.fsGroupChangePolicy 如何影响 volume ownership？
- Vector hit/rank: False / None
- Hybrid hit/rank: True / 3
- Vector retrieved: ['Kubernetes PodSpec.securityContext', 'Kubernetes PodSecurityContext.fsGroup', 'Kubernetes PodSecurityContext.runAsNonRoot']
- Hybrid retrieved: ['Kubernetes PodSecurityContext.fsGroup', 'Kubernetes PodSpec.securityContext', 'Kubernetes PodSecurityContext.fsGroupChangePolicy']
- Judge: `{"vector_only": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "hybrid_rrf": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "winner": "vector_only"}`

### case_15 Kubernetes PodAffinityTerm.matchLabelKeys

- Category: k8s_field
- Question: Kubernetes 字段 PodAffinityTerm.matchLabelKeys 是什么？
- Vector hit/rank: False / None
- Hybrid hit/rank: False / None
- Vector retrieved: ['Kubernetes Affinity.podAffinity', 'Kubernetes Affinity.podAntiAffinity', 'Kubernetes PodSpec.affinity']
- Hybrid retrieved: ['Kubernetes WeightedPodAffinityTerm.podAffinityTerm', 'Kubernetes WeightedPodAffinityTerm.weight', 'Kubernetes Affinity.podAffinity']
- Judge: `{"vector_only": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "hybrid_rrf": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "winner": "tie"}`

### case_16 Kubernetes ServiceSpec.internalTrafficPolicy

- Category: k8s_field
- Question: Kubernetes 字段 ServiceSpec.internalTrafficPolicy 控制什么？
- Vector hit/rank: False / None
- Hybrid hit/rank: False / None
- Vector retrieved: ['Kubernetes ServiceSpec.ports', 'Kubernetes Service.spec', 'Kubernetes ServiceSpec.sessionAffinityConfig']
- Hybrid retrieved: ['Kubernetes ServiceSpec.ports', 'Kubernetes ServiceSpec.sessionAffinityConfig', 'Kubernetes ServiceSpec.sessionAffinity']
- Judge: `{"vector_only": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "hybrid_rrf": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "winner": "tie"}`

### case_17 Kubernetes ServiceSpec.ipFamilyPolicy

- Category: k8s_field
- Question: Kubernetes 字段 ServiceSpec.ipFamilyPolicy 有什么作用？
- Vector hit/rank: False / None
- Hybrid hit/rank: False / None
- Vector retrieved: ['Kubernetes ServiceSpec.ports', 'Kubernetes Service.spec', 'Kubernetes ServiceSpec.sessionAffinityConfig']
- Hybrid retrieved: ['Kubernetes ServiceSpec.ports', 'Kubernetes ServiceSpec.sessionAffinityConfig', 'Kubernetes ServiceSpec.sessionAffinity']
- Judge: `{"vector_only": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "hybrid_rrf": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "winner": "tie"}`

### case_18 Kubernetes ServiceSpec.loadBalancerClass

- Category: k8s_field
- Question: Kubernetes 字段 ServiceSpec.loadBalancerClass 表示什么？
- Vector hit/rank: False / None
- Hybrid hit/rank: False / None
- Vector retrieved: ['Kubernetes ServiceSpec.ports', 'Kubernetes Service.spec', 'Kubernetes ServiceSpec.sessionAffinityConfig']
- Hybrid retrieved: ['Kubernetes ServiceSpec.ports', 'Kubernetes ServiceSpec.sessionAffinityConfig', 'Kubernetes ServiceSpec.sessionAffinity']
- Judge: `{"vector_only": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "hybrid_rrf": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "winner": "tie"}`

### case_19 Kubernetes JobSpec.podReplacementPolicy

- Category: k8s_field
- Question: Kubernetes 字段 JobSpec.podReplacementPolicy 什么时候创建 replacement Pod？
- Vector hit/rank: False / None
- Hybrid hit/rank: True / 3
- Vector retrieved: ['Kubernetes Job.spec', 'Kubernetes JobSpec.selector', 'Kubernetes JobSpec.managedBy']
- Hybrid retrieved: ['Kubernetes JobSpec.selector', 'Kubernetes Job.spec', 'Kubernetes JobSpec.podReplacementPolicy']
- Judge: `{"vector_only": {"correctness": 0, "groundedness": 0, "keypoint_coverage": 0, "identifier_preservation": 0}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "winner": "hybrid_rrf"}`

### case_20 Kubernetes RollingUpdateDeployment.maxUnavailable

- Category: k8s_field
- Question: Kubernetes 字段 RollingUpdateDeployment.maxUnavailable 如何约束 rolling update？
- Vector hit/rank: True / 2
- Hybrid hit/rank: True / 1
- Vector retrieved: ['Kubernetes StatefulSetUpdateStrategy.rollingUpdate', 'Kubernetes RollingUpdateDeployment.maxUnavailable', 'Kubernetes DeploymentStrategy.rollingUpdate']
- Hybrid retrieved: ['Kubernetes RollingUpdateDeployment.maxUnavailable', 'Kubernetes RollingUpdateDeployment.maxSurge', 'Kubernetes DeploymentStrategy.rollingUpdate']
- Judge: `{"vector_only": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 5, "identifier_preservation": 5}, "hybrid_rrf": {"correctness": 5, "groundedness": 5, "keypoint_coverage": 4, "identifier_preservation": 4}, "winner": "vector_only"}`
