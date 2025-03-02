# src/orchestrator/orchestrator.py
from src.storage.document_store import DocumentStore
from src.storage.contact_store import ContactStore
from src.storage.knowledge_graph import KnowledgeGraph
from src.storage.elasticsearch_index import ESIndex
from src.utils.helpers import analyze_sentiment  # Celery task for NLP

class Orchestrator:
    def __init__(self):
        self.doc_store = DocumentStore()
        self.contact_store = ContactStore()
        self.graph = KnowledgeGraph()
        self.es_index = ESIndex()

    def should_process_nlp(self, data):
        """Determine if data should undergo NLP based on content."""
        unstructured = data.get("unstructured", "")
        # Simple heuristic: NLP for text with sentiment-like keywords
        keywords = {"review", "opinion", "great", "bad", "love", "hate"}
        return any(keyword in unstructured.lower() for keyword in keywords) and len(unstructured) > 10

    def process(self, data):
        """Route extracted data to appropriate pipelines."""
        data_type = data.get("type", "mixed")
        result = {}

        # Handle structured data (contacts)
        if "structured" in data_type or data.get("structured"):
            self.contact_store.save(data)
            self.graph.update(data)
            result["contacts_stored"] = True

        # Handle unstructured data (documents)
        if "unstructured" in data_type or data.get("unstructured"):
            doc_id = self.doc_store.save(data)
            result["doc_id"] = doc_id
            # Check if NLP is needed
            if self.should_process_nlp(data):
                analyze_sentiment.delay(data)  # Async NLP processing
                result["nlp_triggered"] = True

        # Index all data in ElasticSearch
        self.es_index.index(data)
        result["indexed"] = True

        return result

# Example usage
if __name__ == "__main__":
    orchestrator = Orchestrator()
    sample_data = {
        "url": "https://example.com",
        "structured": [{"name": "John", "org": "xAI", "email": "john@xai.com"}],
        "unstructured": "This is a great review of the product!",
        "type": "mixed"
    }
    result = orchestrator.process(sample_data)
    print(result)