from worker import job_manager
import time

print("--- JobManager Active Agents ---")
for db_id, agent in job_manager.active_agents.items():
    print(f"DB ID: {db_id} | JobID: {agent.job_id} | State: {agent.state} | Running: {agent.worker_running} | LatestFrame: {agent.latest_frame is not None}")
print(f"Total Active: {len(job_manager.active_agents)}")
