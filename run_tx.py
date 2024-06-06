import neo4j
from neo4j import GraphDatabase

def read_cypher_commands(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        commands = file.read().split(';')
        commands = [cmd.strip() for cmd in commands if cmd.strip()]
    return commands

def send_commands_in_batches(commands, batch_size, driver):
    def execute_batch(tx, batch):
        for command in batch:
            tx.run(command)

    with driver.session() as session:
        for i in range(0, len(commands), batch_size):
            batch = commands[i:i + batch_size]
            session.write_transaction(execute_batch, batch)

def main():
    uri = "bolt://localhost:7687"  # Update with your Neo4j URI
    user = "neo4j"  # Update with your Neo4j user
    password = "password"  # Update with your Neo4j password

    driver = GraphDatabase.driver(uri, auth=(user, password))

    commands_file = 'cypher_commands.txt'
    batch_size = 100  # Adjust the batch size as needed

    cypher_commands = read_cypher_commands(commands_file)
    send_commands_in_batches(cypher_commands, batch_size, driver)

    driver.close()

if __name__ == "__main__":
    main()
