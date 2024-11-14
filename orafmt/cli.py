import subprocess
import sys
from pathlib import Path

def main():
    script_path = Path(__file__).parent / "run-formatter.sh"
    command = ["sh", str(script_path)] + sys.argv[1:]  # Pass all arguments to the script
    result = subprocess.run(command)
    sys.exit(result.returncode)
