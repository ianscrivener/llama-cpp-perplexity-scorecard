import json
from jsonschema import validate, ValidationError

# Load the JSON schema
def main(json_filename,schema_filename):
    with open(schema_filename, 'r') as file:
        schema = json.load(file)

    # Load the JSON file
    with open(json_filename, 'r') as file:
        data = json.load(file)

    # Validate the JSON file with the schema
    try:
        validate(instance=data, schema=schema)
        print("JSON format is valid.")
        return True
    except ValidationError as v:
        print("JSON format is invalid. Error:", v.message)
        return False


