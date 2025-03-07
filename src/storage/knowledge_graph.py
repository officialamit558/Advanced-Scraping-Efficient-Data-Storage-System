# src/storage/knowledge_graph.py
from neo4j import GraphDatabase
from config.config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeGraph:
    def __init__(self):
        """Initialize the Neo4j driver."""
        try:
            self.driver = GraphDatabase.driver(
                Config.NEO4J_URI,
                auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
            )
            logger.info("Connected to Neo4j database at %s", Config.NEO4J_URI)
        except Exception as e:
            logger.error("Failed to connect to Neo4j: %s", e)
            raise

    def update(self, data):
        """Update the knowledge graph with structured data relationships."""
        try:
            structured = data.get("structured", [])
            if not structured:
                logger.info("No structured data provided for Neo4j update")
                return 0

            updated_count = 0
            with self.driver.session() as session:
                for item in structured:
                    name = item.get("name") or "Unknown"
                    org = item.get("org") or "Unknown"
                    email = item.get("email")  # Optional for additional context

                    # Skip if no meaningful data
                    if name == "Unknown" and org == "Unknown":
                        logger.warning("Skipping entry with no name or org: %s", item)
                        continue

                    try:
                        # Merge Person and Company nodes, create WORKS_FOR relationship
                        session.run("""
                            MERGE (p:Person {name: $name})
                            SET p.email = $email
                            MERGE (c:Company {name: $org})
                            MERGE (p)-[r:WORKS_FOR]->(c)
                        """, name=name, org=org, email=email)
                        updated_count += 1
                        logger.debug("Updated graph: %s works for %s", name, org)
                    except Exception as e:
                        logger.error("Error updating graph for %s at %s: %s", name, org, e)

            logger.info("Successfully updated %d relationships in Neo4j", updated_count)
            return updated_count

        except Exception as e:
            logger.error("Failed to update Neo4j graph: %s", e)
            raise

    def close(self):
        """Close the Neo4j driver connection."""
        try:
            self.driver.close()
            logger.info("Neo4j driver connection closed")
        except Exception as e:
            logger.error("Error closing Neo4j connection: %s", e)

# Example usage
if __name__ == "__main__":
    graph = KnowledgeGraph()
    sample_data = {
        "structured": [
            {"name": "John", "org": "xAI", "email": "john@xai.com"},
            {"name": "Jane", "org": "xAI", "email": "jane@xai.com"},
            {"name": None, "org": None}  # Should be skipped
        ]
    }
    updated = graph.update(sample_data)
    print(f"Updated {updated} relationships")
    graph.close()