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
    
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    log_file = open("backend_output.log", "w", buffering=1)
    return subprocess.Popen(
        [venv_python, "-u", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd="backend",
        stdout=log_file,
        stderr=subprocess.STDOUT,
        env=env
    )

def wait_for_backend():
    print("Waiting for application to be ready...")
    for i in range(30):
        try:
            response = requests.get("http://localhost:8000/api/system/health", timeout=2)
            if response.status_code == 200:
                print("Application is online!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if os.path.exists("backend_output.log"):
            with open("backend_output.log", "r") as f:
                content = f.read()
                if "ERROR" in content or "Traceback" in content:
                    # Only show if there's a significant change or error
                    if "address already in use" in content.lower() or "10048" in content:
                        print("Port 8000 is blocked.")
                        return False
        
        time.sleep(2)
        if i % 3 == 0:
            print(f"Still waiting... (Attempt {i+1}/30)")
            
    return False

def main():
    if os.path.exists("backend_output.log"):
        try: os.remove("backend_output.log")
        except: pass

    kill_process_by_name("uvicorn")
    kill_process_by_name("node")
    
    time.sleep(2)
    
    backend_proc = run_backend()
    
    if not wait_for_backend():
        print("Fatal: Application failed to start correctly.")
        if os.path.exists("backend_output.log"):
            with open("backend_output.log", "r") as f:
                print("\n--- Backend Logs ---")
                print(f.read())
        backend_proc.terminate()
        sys.exit(1)
        
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
