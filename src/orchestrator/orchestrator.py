# src/orchestrator/orchestrator.py
from src.storage.document_store import DocumentStore
from src.storage.contact_store import ContactStore
from src.storage.knowledge_graph import KnowledgeGraph
from src.storage.elasticsearch_index import ESIndex
from src.utils.helpers import process_data  # Celery task for NLP
import json
import scrapy

class Orchestrator:
    def __init__(self):
        try:
            self.doc_store = DocumentStore()
            self.contact_store = ContactStore()
            self.graph = KnowledgeGraph()
            self.es_index = ESIndex()
        except Exception as e:
            print(f"Failed to initialize Orchestrator: {e}")
            raise

    def should_process_nlp(self, data):
        """Determine if data should undergo NLP based on content."""
        unstructured = data.get("unstructured", {})
        # Extract text from nested fields (paragraphs, headings)
        text_content = " ".join(
            unstructured.get("paragraphs", []) + unstructured.get("headings", [])
        ).lower()
        # Heuristic: NLP for text with sentiment-like keywords and sufficient length
        keywords = {"review", "opinion", "great", "bad", "love", "hate", "awesome", "terrible"}
        return any(keyword in text_content for keyword in keywords) and len(text_content) > 20

    def process_structured(self, structured_data):
        """Process structured data into contacts format."""
        contacts = []
        # Handle tables (assume rows are contact-like data)
        for table_row in structured_data.get("tables", []):
            # Simple parsing: assume table row contains name, org, email in some form
            try:
                row_text = " ".join(scrapy.Selector(text=table_row).xpath("//text()").getall())
                parts = row_text.split()
                if len(parts) >= 2:  # Basic heuristic for contact data
                    contact = {
                        "name": parts[0],
                        "org": parts[1] if len(parts) > 1 else "Unknown",
                        "email": next((p for p in parts if "@" in p), None)
                    }
                    if contact["email"]:  # Only add if email is found
                        contacts.append(contact)
            except Exception as e:
                print(f"Error parsing table row: {e}")
        
        # Handle lists (assume some items might be contacts)
        for list_item in structured_data.get("lists", []):
            try:
                item_text = scrapy.Selector(text=list_item).xpath("//text()").get(default="")
                if "@" in item_text:  # Look for email-like patterns
                    parts = item_text.split()
                    contacts.append({
                        "name": parts[0] if parts else "Unknown",
                        "org": "Unknown",
                        "email": next((p for p in parts if "@" in p), None)
                    })
            except Exception as e:
                print(f"Error parsing list item: {e}")
        
        return contacts

    def process(self, data):
        """Route extracted data to appropriate pipelines."""
        result = {"url": data.get("url", "unknown")}
        data_type = data.get("type", "mixed")

        try:
            # Handle structured data (contacts)
            structured = data.get("structured", {})
            if "structured" in data_type or structured:
                contacts = self.process_structured(structured)
                if contacts:
                    self.contact_store.save({"structured": contacts})
                    self.graph.update({"structured": contacts})
                    result["contacts_stored"] = len(contacts)
                else:
                    result["contacts_stored"] = 0

            # Handle unstructured data (documents)
            unstructured = data.get("unstructured", {})
            if "unstructured" in data_type or unstructured:
                doc_data = {
                    "url": data["url"],
                    "title": data.get("title", "No title"),
                    "unstructured": unstructured,
                    "depth": data.get("depth", 0)
                }
                doc_id = self.doc_store.save(doc_data)
                result["doc_id"] = str(doc_id)
                # Check if NLP is needed
                if self.should_process_nlp(data):
                    process_data.delay(data)  # Async NLP processing
                    result["nlp_triggered"] = True

            # Handle metadata
            metadata = data.get("metadata", {})
            if metadata:
                result["links_found"] = len(metadata.get("links", []))

            # Index all data in ElasticSearch
            self.es_index.index(data)
            result["indexed"] = True

        except Exception as e:
            print(f"Error processing data for {data['url']}: {e}")
            result["error"] = str(e)

        return result

# Example usage
if __name__ == "__main__":
    orchestrator = Orchestrator()
    sample_data = {
        "url": "https://example.com",
        "title": "Example Page",
        "structured": {
            "tables": ["<tr><td>John</td><td>xAI</td><td>john@xai.com</td></tr>"],
            "lists": ["<li>Jane at xAI - jane@xai.com</li>"]
        },
        "unstructured": {
            "paragraphs": ["This is a great review of the product!"],
            "headings": ["Product Overview"]
        },
        "metadata": {
            "links": ["https://example.com/about", "https://example.com/contact"],
            "meta_tags": ["description", "keywords"]
        },
        "type": "mixed",
        "depth": 0
    }
    result = orchestrator.process(sample_data)
    print(json.dumps(result, indent=2))