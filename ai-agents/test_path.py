import pathlib

# Check the path resolution
file_path = pathlib.Path(__file__)
print(f"Current file: {file_path}")
print(f"Parent: {file_path.parent}")
print(f"Parent.parent: {file_path.parent.parent}")
print(f"Parent.parent.parent: {file_path.parent.parent.parent}")

root_env = file_path.parent.parent / '.env'
print(f"\nLooking for: {root_env}")
print(f"Exists: {root_env.exists()}")

if root_env.exists():
    with open(root_env, 'r') as f:
        for line in f:
            if 'OPENAI_API_KEY' in line:
                print(f"Found OPENAI_API_KEY line: {line[:30]}...")
                break