# tests/run_evals.py
import json
from app.agent.graph import app
from app.database.connection import get_db_schema

def run_evaluations():
    with open("tests/eval_dataset.json") as f:
        benchmarks = json.load(f)

    total = len(benchmarks)
    passed = 0
    recovered_errors = 0

    schema = get_db_schema()

    for idx, test in enumerate(benchmarks):
        config = {"configurable": {"thread_id": f"eval-{idx}"}}
        state = {
            "question": test["question"],
            "schema": schema,
            "sql_query": None,
            "query_result": None,
            "error_message": None,
            "retry_count": 0,
            "final_answer": None
        }

        output = app.invoke(state, config=config)
        answer = output["final_answer"]

        # Check keyword presence in answer
        all_passed = all(kw.lower() in answer.lower() for kw in test["ground_truth_keywords"])
        if all_passed:
            passed += 1

        if output["retry_count"] > 0 and all_passed:
            recovered_errors += 1

    accuracy = (passed / total) * 100
    recovery_rate = (recovered_errors / passed * 100) if passed > 0 else 0

    print("=================== EVALUATION RESULTS ===================")
    print(f"Total Benchmark Cases: {total}")
    print(f"Execution Accuracy:    {accuracy:.2f}%")
    print(f"Self-Corrected Tests:  {recovered_errors}")
    print(f"Recovery Rate:         {recovery_rate:.2f}%")
    print("==========================================================")

if __name__ == "__main__":
    run_evaluations()