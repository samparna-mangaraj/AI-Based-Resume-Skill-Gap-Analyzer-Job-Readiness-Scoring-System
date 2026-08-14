import os
import subprocess
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Move to the backend directory
backend_dir = os.path.join(script_dir, 'backend')
if not os.path.exists(backend_dir):
    print(f"Error: Could not find backend directory at {backend_dir}")
    sys.exit(1)

os.chdir(backend_dir)

# Run the FastAPI server
print("Starting Resume Skill Gap Analyzer...")
try:
    subprocess.run([sys.executable, "-m", "app.main"])
except KeyboardInterrupt:
    print("\nShutting down...")
