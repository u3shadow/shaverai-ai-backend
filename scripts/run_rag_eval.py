import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.rag_evaluator import RagEvaluator
from app.services.rag_service import RagService


def main() -> None:
    service = RagService()
    evaluator = RagEvaluator()

    cases_path = PROJECT_ROOT /"app"/ "tests" / "rag_eval_cases.json"
    with cases_path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    before_recalls = []
    after_recalls = []
    answerable_best_scores = []
    unanswerable_best_scores = []

    for case in cases:
        question = case["question"]
        expected_docs = case["expected_docs"]
        answerable = case["answerable"]

        retrieved = service.retriever.retrieve(
            query=question,
            top_k=20,
        )
        reranked = service.reranker.rerank(
            query=question,
            chunks=retrieved,
        )

        print()
        print("=" * 70)
        print(f'{case["id"]}: {question}')
        print(f"召回数量: {len(retrieved)}")

        if answerable:
            before_recall = evaluator.recall_at_k(
                retrieved, expected_docs, k=5
            )
            after_recall = evaluator.recall_at_k(
                reranked, expected_docs, k=5
            )
            before_rank = evaluator.find_first_rank(
                retrieved, expected_docs
            )
            after_rank = evaluator.find_first_rank(
                reranked, expected_docs
            )

            before_recalls.append(before_recall)
            after_recalls.append(after_recall)

            if reranked:
                answerable_best_scores.append(reranked[0].rerank_score)

            print(f"正确文档首位排名: {before_rank} -> {after_rank}")
            print(f"Recall@5: {before_recall:.2f} -> {after_recall:.2f}")

        else:
            best_score = reranked[0].rerank_score if reranked else 0.0
            unanswerable_best_scores.append(best_score)
            print(f"知识库外问题最高 rerank_score: {best_score:.4f}")

    if before_recalls:
        print()
        print("=" * 70)
        print(f"平均 Recall@5（重排前）: {sum(before_recalls) / len(before_recalls):.3f}")
        print(f"平均 Recall@5（重排后）: {sum(after_recalls) / len(after_recalls):.3f}")

    if answerable_best_scores and unanswerable_best_scores:
        lowest_answerable = min(answerable_best_scores)
        highest_unanswerable = max(unanswerable_best_scores)

        print(f"可回答问题最低最高分: {lowest_answerable:.4f}")
        print(f"不可回答问题最高分: {highest_unanswerable:.4f}")

        if highest_unanswerable < lowest_answerable:
            candidate = (highest_unanswerable + lowest_answerable) / 2
            print(f"可以进一步试验的阈值候选: {candidate:.4f}")
        else:
            print("两类问题分数有重叠，当前数据无法支持单一可靠阈值。")


if __name__ == "__main__":
    main()