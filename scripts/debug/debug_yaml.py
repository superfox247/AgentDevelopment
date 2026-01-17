import sys

import yaml

file_path = "domains/image_gen/image_generator/agent.yaml"
try:
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
        print("--- CONTENT START ---")
        print(content)
        print("--- CONTENT END ---")
        print(f"Hex: {content.encode('utf-8').hex()}")
        yaml.safe_load(content)
    print("YAML parsed successfully!")
except Exception as e:
    print(f"Error parsing YAML: {e}")
    sys.exit(1)
