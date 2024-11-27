import json
import sys

def jsonl_to_json(input_file, output_file):
    # List to store all JSON objects
    json_objects = []
    
    # Read JSONL file and parse each line
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                json_objects.append(json.loads(line))
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_objects, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python jsonl2json.py input.jsonl output.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        jsonl_to_json(input_file, output_file)
        print(f"Successfully converted {input_file} to {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
