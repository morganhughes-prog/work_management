import os

# Configuration
# The directory where the script is located (your project root)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = "project_code_bundle.txt"

# Files with these extensions will be included
TARGET_EXTENSIONS = {'.py', '.html', '.css'}

# Directories to entirely skip (like virtual environments or git folders)
IGNORE_DIRS = {'venv', '.venv', '__pycache__', '.git', '.vscode'}

# Files to skip (like this script itself and the output file)
IGNORE_FILES = {'bundle_project.py', OUTPUT_FILE, 'requirements.txt'}

def bundle_files():
    print(f"Scanning project directory: {PROJECT_ROOT}")
    print("Bundling files... Please wait.")
    
    file_count = 0
    
    with open(os.path.join(PROJECT_ROOT, OUTPUT_FILE), 'w', encoding='utf-8') as outfile:
        # Walk through all directories and subdirectories
        for root, dirs, files in os.walk(PROJECT_ROOT):
            # Modify dirs in-place to skip ignored directories entirely
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file in IGNORE_FILES:
                    continue
                    
                # Check if file extension matches our target list
                _, ext = os.path.splitext(file)
                if ext.lower() in TARGET_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    
                    # Get the relative path starting from the project folder
                    relative_path = os.path.relpath(full_path, PROJECT_ROOT)
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='replace') as infile:
                            content = infile.read()
                            
                        # Write the separating header and relative file path
                        outfile.write("========================\n")
                        outfile.write(f"FILE: {relative_path}\n")
                        outfile.write("========================\n\n")
                        
                        # Append the actual code/content
                        outfile.write(content)
                        outfile.write("\n\n") # Add blank lines before the next file
                        
                        file_count += 1
                        print(f"Appended: {relative_path}")
                        
                    except Exception as e:
                        print(f"Error reading {relative_path}: {e}")
                        
    print("---")
    print(f"Success! {file_count} files bundled into '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    bundle_files()