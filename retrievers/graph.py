import json
import spacy
from neo4j import GraphDatabase

nlp = spacy.load("en_core_web_sm")

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "AllyInpwd"))

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in {"PERSON", "ORG"}]

def create_graph(tx, doc_id, title, entities):
    tx.run("MERGE (d:Document {id: $id, title: $title})", id=doc_id, title=title)

    for entity, label in entities:
        node_type = "Person" if label == "PERSON" else "Company"
        tx.run(f"MERGE (e:{node_type} {{name: $name}})", name=entity)
        tx.run(f"""
            MATCH (d:Document {{id: $doc_id}})
            MATCH (e:{node_type} {{name: $name}})
            MERGE (d)-[:MENTIONS]->(e)
        """, doc_id=doc_id, name=entity)

def populate_graph_from_docs():  # <-- 🔁 Manual call
    with open('ingest/parsed_docs.jsonl', 'r', encoding='utf-8') as f:
        docs = [json.loads(line) for line in f]

    with driver.session() as session:
        for doc in docs:
            entities = extract_entities(doc["body"])
            session.write_transaction(create_graph, doc["doc_id"], doc["title"], entities)

    print("Entities extracted and added to Neo4j.")

def run_graph_query(query):
    if "company" in query.lower() or "mention" in query.lower():
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "AllyInpwd"))
        with driver.session() as session:
            result = session.run("""
                MATCH (d:Document)-[:MENTIONS]->(e)
                RETURN d.title AS document, collect(e.name) AS mentions
            """)
            return "\n".join([
                f"{row['document']} mentions: {', '.join(row['mentions'])}"
                for row in result
            ])
    return "Graph query not understood."

if __name__ == "__main__":
    populate_graph_from_docs()
