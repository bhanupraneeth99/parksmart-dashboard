import os
import subprocess
import time
import sys
import webbrowser
import requests

def kill_process_by_name(name):
    print(f"Cleaning up existing {name} processes...")
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", f"{name}.exe", "/T"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", name], capture_output=True)
    except Exception:
        pass

def run_backend():
    print("Starting Unified Smart Parking Application...")
    venv_python = os.path.join("backend", "venv", "Scripts", "python.exe") if sys.platform == "win32" else os.path.join("backend", "venv", "bin", "python")
    if not os.path.exists(venv_python):
        print("Backend virtual environment not found. Please run setup first.")
        sys.exit(1)
    
    # Run uvicorn in a separate process
    return subprocess.Popen(
        [venv_python, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd="backend"
    )

def wait_for_backend():
    print("Waiting for application to be ready...")
    for _ in range(30):
        try:
            response = requests.get("http://localhost:8000/api/system/health", timeout=2)
            if response.status_code == 200:
                print("Application is online!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    return False

def main():
    # 1. Cleanup
    kill_process_by_name("uvicorn")
    kill_process_by_name("node")
    
    # 2. Start Unified Backend (Serves Frontend)
    backend_proc = run_backend()
    
    # 3. Wait for Readiness
    if not wait_for_backend():
        print("Timeout: Application failed to start.")
        backend_proc.terminate()
        sys.exit(1)
        
    # 4. Open Browser to Unified URL
    print("Launching Integrated Dashboard...")
    webbrowser.open("http://localhost:8000/admin")
    
    print("\n--- Project is running as a Single Application on Port 8000! ---")
    print("Press Ctrl+C to stop the application.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping application...")
        backend_proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
