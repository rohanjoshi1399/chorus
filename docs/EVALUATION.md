# Evaluation Guide

## Overview

RAG evaluation metrics and methodology for achieving 90% precision.

---

## Key Metrics

### Retrieval Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Precision@K** | relevant_in_topK / K | ≥ 0.90 |
| **Recall@K** | relevant_in_topK / total_relevant | ≥ 0.85 |
| **MRR** | 1 / first_relevant_rank | ≥ 0.80 |

### Generation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Faithfulness** | Answer grounded in context | ≥ 0.95 |
| **Answer Relevancy** | Answer addresses query | ≥ 0.90 |
| **Context Relevancy** | Context supports answer | ≥ 0.85 |

---

## Evaluation API

```python
from src.evaluation import rag_evaluator

result = await rag_evaluator.evaluate(
    query="How does LangGraph handle state?",
    answer="LangGraph uses TypedDict...",
    retrieved_docs=docs,
    relevant_doc_ids=["doc1", "doc2"],  # Ground truth
)

print(f"Precision@5: {result.precision_at_k}")
print(f"Faithfulness: {result.faithfulness}")
print(f"Overall: {result.overall_score}")
```

---

## Batch Evaluation

```python
test_cases = [
    {"query": "...", "answer": "...", "retrieved_docs": [...], "relevant_ids": [...]},
    # More test cases...
]

results = await rag_evaluator.batch_evaluate(test_cases)
print(f"Avg Precision@5: {results['avg_precision_at_k']}")
print(f"Avg Faithfulness: {results['avg_faithfulness']}")
```

---

## Query Rewrite Impact

The query rewrite loop improves precision by:

1. **Grading** retrieved documents (LLM judge)
2. **Rewriting** poor queries with synonyms, specificity
3. **Retrying** up to 2 times before proceeding

Expected improvement: 70-80% → 90%+ precision

---

## Creating Test Datasets

```python
# Gold standard dataset format
gold_dataset = [
    {
        "query": "What is LangGraph?",
        "relevant_doc_ids": ["langraph_intro", "langraph_overview"],
        "expected_answer_contains": ["state machine", "workflow"]
    }
]
```
