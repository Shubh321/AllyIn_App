import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retrievers.sql import run_sql_query
from retrievers.vectors import semantic_search

def route_question(question):
    if any(keyword in question.lower() for keyword in ["customer", "order", "amount", "spent", "date"]):
        print("🔍 Using SQL Retriever")
        return run_sql_query(question)
    else:
        print("🧠 Using Vector Search")
        results = semantic_search(question)
        return "\n".join([f"{r['title']} – {r['created_at']}\n{r.get('body', '')[:150]}..." for r in results]) or "No relevant semantic matches found."
if __name__ == "__main__":
    print(route_question("Which customer spent the most money?"))
    print()
    print(route_question("What was the email about OpenAI's announcement?"))
