# Enterprise RAG Evaluation Template

## Purpose
This file is used to benchmark the current RAG system from three angles:

1. Retrieval quality
2. Final answer quality
3. End-to-end latency

It is designed for small-scale local evaluation and can be used for:
- project README metrics
- resume bullets
- interview explanation
- version comparison (v1.0 / v1.2 / v1.4 / future versions)

---

## Recommended Evaluation Process

For each question:

1. Ask the question through the frontend or `/ask` API.
2. Record:
   - whether the top-1 source is correct
   - whether the final answer is correct / mostly correct / incorrect
   - total response time
3. Repeat for all test questions.
4. Compute final metrics.

---

## Suggested Metrics

### 1. Top-1 Retrieval Accuracy
Definition:
- Whether the first retrieved source chunk belongs to the correct document / correct topic.

Formula:
- Top-1 Retrieval Accuracy = correct_top1 / total_questions

### 2. Answer Correctness
Suggested labels:
- Correct
- Partially Correct
- Incorrect

Optional scoring:
- Correct = 1
- Partially Correct = 0.5
- Incorrect = 0

Formula:
- Answer Score = total_answer_points / total_questions

### 3. Average Response Time
Definition:
- End-to-end time from user submit to answer returned.

Formula:
- Avg Latency = total_latency / total_questions

---

## Test Set

Use the CSV file in the same folder:
- `enterprise_rag_eval_questions.csv`

It contains 10 questions:
- CUDA / GPU memory questions
- internal policy questions
- RAG / API document questions

You can expand it later.

---

## Manual Evaluation Table

| QID | Question | Expected Topic | Top-1 Correct | Answer Label | Answer Score | Latency (s) | Notes |
|---|---|---|---|---|---:|---:|---|
| 1 | Bank Conflict 是什么？ | CUDA |  |  |  |  |  |
| 2 | CUDA 里共享内存有什么作用？ | CUDA |  |  |  |  |  |
| 3 | 怎样减少显存访问带来的性能问题？ | CUDA |  |  |  |  |  |
| 4 | Global Memory 的优化重点是什么？ | CUDA |  |  |  |  |  |
| 5 | 公司数据分为几个等级？ | Policy |  |  |  |  |  |
| 6 | 哪些数据属于 L3 机密数据？ | Policy |  |  |  |  |  |
| 7 | 是否允许把机密代码粘贴到外部 AI 助手？ | Policy |  |  |  |  |  |
| 8 | 这个文档解析服务支持什么能力？ | API Doc |  |  |  |  |  |
| 9 | RAG 系统为什么需要来源追踪？ | RAG / API Doc |  |  |  |  |  |
| 10 | Hybrid Retrieval 的作用是什么？ | RAG |  |  |  |  |  |

---

## Final Summary Template

After finishing the table, fill this section:

### Version
- Current version: `v1.4`

### Test Scale
- Number of evaluation questions: `10`

### Results
- Top-1 Retrieval Accuracy: `__/10 = __%`
- Answer Correctness Score: `__/10 = __`
- Average End-to-End Latency: `__ s`

### Example Resume-ready Metrics
Use only real measured results.

Examples:
- Improved Top-1 retrieval accuracy from **60% to 90%** on a 10-question internal benchmark after adding Hybrid Retrieval and reranking.
- Delivered a full-stack local RAG MVP with **~2.0s average response latency** on a consumer GPU setup.
- Built a hybrid retrieval pipeline that reduced noisy top-ranked results in Chinese QA scenarios.

---

## Interview-ready Explanation

You can explain the benchmark like this:

> To make the project more credible, I built a small evaluation set with 10 domain-specific questions and tracked three metrics: Top-1 retrieval accuracy, answer correctness, and end-to-end latency. This helped me compare dense-only retrieval, hybrid retrieval, and reranking strategies in a structured way.

中文版：

> 为了让项目结果更可信，我基于当前知识库构建了一组 10 道测试问题，主要衡量 Top-1 检索准确率、回答正确性和端到端响应时间，并用这组数据对比了 Dense Only、Hybrid Retrieval 和 Reranker 方案的效果差异。

---

## Next Step (Optional)
Later you can extend this into:
- automated evaluation script
- version-to-version benchmark comparison
- JSON logging
- dashboard visualization
