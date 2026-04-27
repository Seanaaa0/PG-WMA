import os
import re
import json
from pathlib import Path

# 👉 這裡放你要分析的資料夾（可以多個）
LOG_DIRS = [
    "outputs/rule_v6a_20x20_1",
    "outputs/predictive_v8_20x20_1",
    "outputs/predictive_llm_v8_20x20_1",
    "outputs/rule_v6a_20x20_2",
    "outputs/rule_v6a_25x25_1",
]


def analyze_single_dir(log_dir):
    success_count = 0
    fail_count = 0
    steps_list = []

    for file in os.listdir(log_dir):
        if not file.endswith(".txt"):
            continue

        path = os.path.join(log_dir, file)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        result_match = re.search(r"RESULT:\s*(SUCCESS|FAIL)", text)
        steps_match = re.search(r"STEPS:\s*(\d+)", text)

        if not result_match:
            continue

        result = result_match.group(1)

        if result == "SUCCESS":
            success_count += 1
            if steps_match:
                steps_list.append(int(steps_match.group(1)))
        else:
            fail_count += 1

    total = success_count + fail_count

    result = {
        "dir": log_dir,
        "total": total,
        "success": success_count,
        "fail": fail_count,
        "success_rate": success_count / total if total > 0 else 0.0,
    }

    if steps_list:
        result.update({
            "avg_steps": sum(steps_list) / len(steps_list),
            "min_steps": min(steps_list),
            "max_steps": max(steps_list),
        })

    return result


def main():
    all_results = {}

    for log_dir in LOG_DIRS:
        res = analyze_single_dir(log_dir)

        name = Path(log_dir).name
        all_results[name] = res

        print("\n==============================")
        print("DIR:", name)
        print("==============================")
        print(res)

        # 👉 每個資料夾各存一份
        output_path = Path(log_dir) / "summary.json"
        with open(output_path, "w") as f:
            json.dump(res, f, indent=2)

    # 🔥 總統計（跨資料夾）
    overall = {
        "experiments": all_results
    }

    output_all = Path("outputs") / "benchmark_summary.json"
    with open(output_all, "w") as f:
        json.dump(overall, f, indent=2)

    print("\n==============================")
    print("ALL SUMMARY SAVED TO:", output_all)
    print("==============================")


if __name__ == "__main__":
    main()
