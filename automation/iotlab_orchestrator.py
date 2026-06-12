#!/usr/bin/env python3
import os
import sys
import time
import json
import subprocess
from iotlabcli import auth, experiment, node

# --- Experiment Constants ---
EXP_NAME = "FL_IFAshield_Scale_100"
DURATION = 1440  # 24 Hours continuous run time
SITE_1 = "grenoble"
SITE_2 = "lille"
NODE_TYPE = "a8"  # ARMv8 Cortex-A53 nodes

def authenticate_session():
    """Verifies or triggers FIT/IoT-LAB API authentication credentials."""
    try:
        username, _ = auth.get_user()
        print(f"[+] Authenticated to IoT-LAB as user: {username}")
    except Exception:
        print("[-] Authentication missing. Please run 'iotlab-auth -u <user>' first.")
        sys.exit(1)

def submit_physical_experiment():
    """Submits a 100 physical heterogeneous node allocation request across clusters."""
    print(f"[+] Submitting physical testbed allocation request: {EXP_NAME}...")
    
    # Allocating 50 nodes from Grenoble and 50 nodes from Lille for network heterogeneity
    resources = [
        experiment.exp_resources(nodes=f"site={SITE_1}+type={NODE_TYPE},0-49"),
        experiment.exp_resources(nodes=f"site={SITE_2}+type={NODE_TYPE},0-49")
    ]
    
    # Create experiment profile definition
    exp_def = experiment.experiment_to_json(EXP_NAME, DURATION, resources)
    
    # Submit via REST CLI client
    api = experiment.get_api()
    exp_data = experiment.submit_experiment(api, exp_def)
    exp_id = exp_data['id']
    print(f"[+] Experiment submitted successfully! Assigned EXP_ID: {exp_id}")
    return exp_id

def wait_for_boot_state(exp_id):
    """Blocks execution until all 100 bare-metal physical routers are in 'Running' state."""
    print("[*] Waiting for node infrastructure allocation and state initialization...")
    api = experiment.get_api()
    while True:
        status = experiment.get_experiment(api, exp_id, 'state')
        state = status['state']
        if state == "Running":
            print("[+] Infrastructure successfully provisioned and online.")
            break
        elif state in ["Error", "Terminated"]:
            print(f"[-] Infrastructure allocation failed with status state: {state}")
            sys.exit(1)
        time.append(15)

def map_topology_roles(exp_id):
    """Maps the 100 nodes into the 60 Edge Router, 20 Consumer, 20 Attacker split matrix."""
    api = experiment.get_api()
    nodes_list = node.get_nodes(api, exp_id)
    
    # Extract string hostnames (e.g., node-a8-1.grenoble.iot-lab.info)
    hosts = sorted([f"node-{n['network_address']}" for n in nodes_list['items']])
    
    topology = {
        "routers": hosts[0:60],     # 60 nodes executing local learning & mitigation pipelines
        "consumers": hosts[60:80],  # 20 nodes generating benign Zipfian interest distribution profiles
        "attackers": hosts[80:100]  # 20 nodes orchestrating peripheral/collusive IFA campaigns
    }
    
    with open("topology_matrix.json", "w") as f:
        json.dump(topology, f, indent=4)
    print("[+] Created topology network matrix blueprint 'topology_matrix.json'.")
    return topology

def deploy_provisioning_payload(topology):
    """Uses parallelized SSH/SCP execution vectors to provision nodes with requirements."""
    print("[+] Launching asynchronous edge software deployment via Ansible/Parallel-SSH...")
    
    # Write host files out for automation engine targets
    for role, target_hosts in topology.items():
        with open(f"hosts_{role}.txt", "w") as f:
            f.write("\n".join(target_hosts))
            
    # Bootstrap deployment on routers via execution wrapper
    print("[*] Provisioning NFD stack + Python mobile libraries onto Edge Routers...")
    subprocess.run(["ansible-playbook", "-i", "hosts_routers.txt", "provision_edge.yml"])
    
    print("[+] Infrastructure orchestration phase complete. FL-IFAshield operational.")

if __name__ == "__main__":
    authenticate_session()
    exp_id = submit_physical_experiment()
    wait_for_boot_state(exp_id)
    topo = map_topology_roles(exp_id)
    deploy_provisioning_payload(topo)