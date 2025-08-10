import time
import subprocess
import sys

def run_daemon():
    while True:
        print("Running main.py checks...")
        # Use sys.executable to run main.py with the same Python interpreter
        result = subprocess.run([sys.executable, "main.py"])
        
        if result.returncode != 0:
            print("Error: main.py exited with code", result.returncode)
        
        time.sleep(90)

if __name__ == "__main__":
    run_daemon()
