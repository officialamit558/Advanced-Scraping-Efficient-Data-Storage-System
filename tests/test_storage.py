# Unit tests for storage
# tests/test_storage.py
import pytest
from src.storage.document_store import DocumentStore
from src.storage.contact_store import ContactStore
from src.storage.knowledge_graph import KnowledgeGraph
from src.storage.elasticsearch_index import ESIndex
import time

# Fixtures for storage classes
@pytest.fixture
def doc_store():
    return DocumentStore()

@pytest.fixture
def contact_store():
    return ContactStore()

@pytest.fixture
def knowledge_graph():
    kg = KnowledgeGraph()
    yield kg
    kg.close()

@pytest.fixture
def es_index():
    return ESIndex()

# Unit Test: Test document storage in MongoDB
def test_document_store_save(doc_store):
    data = {"unstructured": "Test content", "url": "https://example.com"}
    doc_id = doc_store.save(data)
    
    result = doc_store.collection.find_one({"_id": doc_id})
    assert result["content"] == "Test content"
    assert result["source"] == "https://example.com"

# Unit Test: Test contact storage in PostgreSQL
def test_contact_store_save(contact_store):
    data = {"structured": [{"name": "John", "org": "xAI", "email": "john@xai.com"}]}
    contact_store.save(data)
    
    contact_store.cursor.execute("SELECT * FROM contacts WHERE name = 'John'")
    result = contact_store.cursor.fetchone()
    assert result[1] == "John"  # Assuming id, name, org, email, metadata order
    assert result[2] == "xAI"

# Unit Test: Test knowledge graph updates in Neo4j
def test_knowledge_graph_update(knowledge_graph):
    data = {"structured": [{"name": "John", "org": "xAI"}]}
    knowledge_graph.update(data)
    
    with knowledge_graph.driver.session() as session:
        result = session.run("MATCH (p:Person {name: 'John'})-[:WORKS_FOR]->(c:Company {name: 'xAI'}) RETURN p, c")
        assert result.single() is not None

# Unit Test: Test ElasticSearch indexing
def test_elasticsearch_index(es_index):
    data = {"url": "https://example.com", "unstructured": "Search me"}
    es_index.index(data)
    
    # Wait briefly for indexing
    time.sleep(1)
    result = es_index.es.search(index="scraped_data", body={"query": {"match": {"content": "Search me"}}})
    assert result["hits"]["total"]["value"] > 0

# Stress Test: Test storage under high load
def test_stress_storage(doc_store, contact_store, knowledge_graph, es_index):
    # Generate 1000 sample data entries
    sample_data = [
        {
            "url": f"https://example.com/{i}",
            "unstructured": f"Content {i}",
            "structured": [{"name": f"User{i}", "org": "TestOrg", "email": f"user{i}@test.com"}]
        }
        for i in range(1000)
    ]
    
    start_time = time.time()
    for data in sample_data:
        doc_store.save(data)
        contact_store.save(data)
        knowledge_graph.update(data)
        es_index.index(data)
    duration = time.time() - start_time
    
    # Verify data was stored
    doc_count = doc_store.collection.count_documents({})
    contact_store.cursor.execute("SELECT COUNT(*) FROM contacts")
    contact_count = contact_store.cursor.fetchone()[0]
    with knowledge_graph.driver.session() as session:
        kg_count = session.run("MATCH (p:Person)-[:WORKS_FOR]->(c:Company) RETURN COUNT(p)").single()[0]
    es_count = es_index.es.count(index="scraped_data")["count"]
    
    assert doc_count == 1000
    assert contact_count == 1000
    assert kg_count > 0  # At least some relationships
    assert es_count == 1000
    
    # Check performance (e.g., under 30 seconds for 1000 entries)
    assert duration < 30, f"Stress test took too long: {duration} seconds"

if __name__ == "__main__":
    pytest.main(["-v"])