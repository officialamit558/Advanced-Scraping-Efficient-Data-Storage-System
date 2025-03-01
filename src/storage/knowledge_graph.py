# Neo4j for relationships
# src/storage/knowledge_graph.py
from neo4j import GraphDatabase
from config.config import Config

class KnowledgeGraph:
    def __init__(self):
        self.driver = GraphDatabase.driver(Config.NEO4J_URI, auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD))

    def update(self, data):
        with self.driver.session() as session:
            structured = data.get("structured", [])
            for item in structured:
                session.run("""
                    MERGE (p:Person {name: $name})
                    MERGE (c:Company {name: $org})
                    MERGE (p)-[:WORKS_FOR]->(c)
                """, name=item.get("name"), org=item.get("org"))

    def close(self):
        self.driver.close()

# Example usage
if __name__ == "__main__":
    graph = KnowledgeGraph()
    graph.update({"structured": [{"name": "John", "org": "xAI"}]})
    graph.close()