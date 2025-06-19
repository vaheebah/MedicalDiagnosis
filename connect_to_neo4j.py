#TASK1
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "neo4j12345"

driver = GraphDatabase.driver(uri, auth=(username, password))

def test_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Connected to Neo4j!' AS message")
        print(result.single()["message"])

test_connection()
