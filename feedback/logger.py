
import json
from datetime import datetime

def log_feedback(question, answer, feedback_type, correction=None):
    entry = {
        "question": question,
        "answer": answer,
        "feedback": feedback_type,
        "timestamp": datetime.now().isoformat()
    }
    if correction:
        entry["correction"] = correction

    with open("feedback_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

