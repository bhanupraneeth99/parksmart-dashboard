import requests
import time
import json

def track():
    print("Starting tracking...")
    # Trigger job
    r = requests.post('http://127.0.0.1:8000/api/jobs/start-demo', json={'video': 'parking_video.mp4'})
    print(f"Trigger Status: {r.status_code}")
    
    start_time = time.time()
    last_states = {}
    
    # Track for 60 seconds
    while time.time() - start_time < 60:
        r = requests.get('http://127.0.0.1:8000/api/slots')
        if r.status_code == 200:
            slots = r.json()
            current_states = {s['id']: s['status'] for s in slots}
            if current_states != last_states:
                print(f"Time: {int(time.time() - start_time)}s - States: {current_states}")
                last_states = current_states
        
        r = requests.get('http://127.0.0.1:8000/api/system/health')
        health = r.json()
        if health.get('worker_state') == 'IDLE' and last_states:
             # If it just finished, break
             if time.time() - start_time > 10:
                 print("Job finished.")
                 break
        
        time.sleep(1)

if __name__ == "__main__":
    # Start server in background if not running? 
    # Assumes server is already running.
    track()
