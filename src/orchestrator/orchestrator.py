# Data routing agent
# src/orchestrator/orchestrator.py
from src.storage.document_store import DocumentStore
from src.storage.contact_store import ContactStore  # Still works with MySQL version
from src.storage.knowledge_graph import KnowledgeGraph
from src.storage.elasticsearch_index import ESIndex

class Orchestrator:
    def __init__(self):
        self.doc_store = DocumentStore()
        self.contact_store = ContactStore()
        self.graph = KnowledgeGraph()
        self.es_index = ESIndex()

    def process(self, data):
        data_type = data.get("type", "mixed")
        
        if "structured" in data_type or data.get("structured"):
            self.contact_store.save(data)
            self.graph.update(data)
        if "unstructured" in data_type or data.get("unstructured"):
            self.doc_store.save(data)
            if "review" in data.get("unstructured", "").lower():
                return True  # Signal NLP
        self.es_index.index(data)
        return False

# Example usage
if __name__ == "__main__":
    orchestrator = Orchestrator()
    needs_nlp = orchestrator.process({"url": "https://example.com", "unstructured": "Great review!", "type": "unstructured"})
    print(f"Needs NLP: {needs_nlp}")