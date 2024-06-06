import csv

# Define function to parse distelec.txt
def parse_distelec(file_path):
    distelec_data = {}
    with open(file_path, 'r', encoding='latin1') as file:
        reader = csv.reader(file)
        for row in reader:
            codele = row[0].strip()
            provincia = row[1].strip()
            canton = row[2].strip()
            distrito = row[3].strip()
            distelec_data[codele] = {
                'provincia': provincia,
                'canton': canton,
                'distrito': distrito
            }
    return distelec_data

# Define function to parse padron.txt
def parse_padron(file_path):
    padron_data = []
    with open(file_path, 'r', encoding='latin1') as file:
        reader = csv.reader(file)
        for row in reader:
            padron_data.append({
                'cedula': row[0].strip(),
                'codelec': row[1].strip(),
                'junta': row[4].strip(),
                'nombre': row[5].strip(),
                'apellido1': row[6].strip(),
                'apellido2': row[7].strip()
            })
    return padron_data

# Define function to generate Cypher code
def generate_cypher(distelec_data, padron_data):
    cypher_commands = []

    # Create nodes for provincias, cantones, distritos, juntas
    provincias = set()
    cantones = set()
    distritos = set()
    juntas = set()

    for entry in distelec_data.values():
        provincias.add(entry['provincia'])
        cantones.add((entry['canton'], entry['provincia']))
        distritos.add((entry['distrito'], entry['canton'], entry['provincia']))

    for persona in padron_data:
        juntas.add(persona['junta'])

    for provincia in provincias:
        cypher_commands.append(f"CREATE (:Provincia {{nombre: '{provincia}'}});")

    for canton, provincia in cantones:
        cypher_commands.append(f"CREATE (:Canton {{nombre: '{canton}', provincia: '{provincia}'}});")

    for distrito, canton, provincia in distritos:
        cypher_commands.append(f"CREATE (:Distrito {{nombre: '{distrito}', canton: '{canton}', provincia: '{provincia}'}});")

    for junta in juntas:
        cypher_commands.append(f"CREATE (:Junta {{numero: '{junta}'}});")

    # Create nodes and relationships for personas
    for persona in padron_data:
        distelec = distelec_data[persona['codelec']]
        cypher_commands.append(
            f"CREATE (p:Persona {{cedula: '{persona['cedula']}', nombre: '{persona['nombre']}', "
            f"apellido1: '{persona['apellido1']}', apellido2: '{persona['apellido2']}'}});"
        )
        cypher_commands.append(
            f"MATCH (p:Persona {{cedula: '{persona['cedula']}'}}), (j:Junta {{numero: '{persona['junta']}'}}) "
            f"CREATE (p)-[:VOTA_EN]->(j);"
        )
        cypher_commands.append(
            f"MATCH (p:Persona {{cedula: '{persona['cedula']}'}}), (d:Distrito {{nombre: '{distelec['distrito']}'}}) "
            f"CREATE (p)-[:VIVE_EN]->(d);"
        )
        cypher_commands.append(
            f"MATCH (d:Distrito {{nombre: '{distelec['distrito']}'}}), (c:Canton {{nombre: '{distelec['canton']}'}}) "
            f"CREATE (d)-[:PARTE_DE]->(c);"
        )
        cypher_commands.append(
            f"MATCH (c:Canton {{nombre: '{distelec['canton']}'}}), (p:Provincia {{nombre: '{distelec['provincia']}'}}) "
            f"CREATE (c)-[:CANTON_DE]->(p);"
        )

    return '\n'.join(cypher_commands)

# Main function to process files and generate Cypher code
def main():
    distelec_file = 'distelec.txt'
    padron_file = 'padron.txt'


    distelec_data = parse_distelec(distelec_file)
    padron_data = parse_padron(padron_file)

    cypher_code = generate_cypher(distelec_data, padron_data)

    with open('cypher_commands.txt', 'w', encoding='utf-8') as output_file:
        output_file.write(cypher_code)

    print("Cypher commands have been generated and saved to cypher_commands.txt")

if __name__ == "__main__":
    main()
