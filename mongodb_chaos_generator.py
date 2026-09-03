#!/usr/bin/env python3
"""
MongoDB Sharded Cluster Chaos Engineering & Disaster Simulation Generator
Injects controlled failure scenarios into the local 14-node Docker environment
for engineering training, troubleshooting, and RCA practice.
"""

import sys
import time
import argparse
import subprocess

def run_cmd(cmd, check=True):
    print(f"Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"Warning/Error: {res.stderr.strip()}")
    return res.stdout.strip()

def chaos_scenario_1_primary_crash():
    print("\n--- [CHAOS SCENARIO 1] Primary Node Crash (Shard 01) ---")
    print("Action: Stopping 's1-node1' container abruptly...")
    run_cmd("docker stop s1-node1", check=False)
    print("Target Impact: Shard 01 Primary down. Re-election triggered among s1-node2 & s1-node3.")
    print("Engineer Goal: Verify election time in app logs, identify new Primary, and restore s1-node1.")

def chaos_scenario_2_csrs_majority_loss():
    print("\n--- [CHAOS SCENARIO 2] CSRS Majority Loss (Metadata Read-Only) ---")
    print("Action: Stopping 'csrs02' and 'csrs03' containers...")
    run_cmd("docker stop csrs02 csrs03", check=False)
    print("Target Impact: CSRS lost quorum (1/3 remaining). Metadata is locked in READ-ONLY mode.")
    print("Engineer Goal: Diagnose 'ConfigServerUnreachable' on mongos, perform force reconfig on csrs01, and recover cluster.")

def chaos_scenario_3_oplog_rollover_burst():
    print("\n--- [CHAOS SCENARIO 3] Rapid Oplog Flooding (Reporting Pipeline Disruption) ---")
    print("Action: Injecting 100,000 document write burst to force oplog rollover...")
    script = """
    docker exec -i mongos01 mongosh --port 27017 --eval '
    use chaos_test_db;
    var docs = [];
    for (let i=0; i<50000; i++) {
        docs.push({ padding: "X".repeat(1024), ts: new Date(), seq: i });
        if (i % 10000 === 0) { db.heavy_writes.insertMany(docs); docs = []; }
    }
    '
    """
    run_cmd(script, check=False)
    print("Target Impact: Rapid oplog consumption. Tailing change stream consumers fall behind/invalidate.")
    print("Engineer Goal: Detect oplog duration depletion and execute replSetResizeOplog + minRetentionHours fix.")

def chaos_scenario_4_jumbo_chunk_injection():
    print("\n--- [CHAOS SCENARIO 4] Jumbo Chunk Generation & Balancer Stall ---")
    print("Action: Inserting 50,000 documents with non-cardinal shard key...")
    script = """
    docker exec -i mongos01 mongosh --port 27017 --eval '
    sh.enableSharding("chaos_jumbo_db");
    sh.shardCollection("chaos_jumbo_db.orders", { account_type: 1 });
    var docs = [];
    for (let i=0; i<30000; i++) {
        docs.push({ account_type: "VIP_CORPORATE", data: "Y".repeat(500) });
        if (i % 5000 === 0) { db.getSiblingDB("chaos_jumbo_db").orders.insertMany(docs); docs = []; }
    }
    '
    """
    run_cmd(script, check=False)
    print("Target Impact: Single chunk exceeds 64MB and gets marked 'jumbo'. Balancer stalls on chunk.")
    print("Engineer Goal: Identify jumbo chunk in sh.status(), split chunk, and refine shard key.")

def chaos_scenario_5_mongos_router_crash():
    print("\n--- [CHAOS SCENARIO 5] Primary Query Router Outage ---")
    print("Action: Stopping 'mongos01' router container...")
    run_cmd("docker stop mongos01", check=False)
    print("Target Impact: mongos01 unreachable. Client connection pool fails if not using router list/HAProxy.")
    print("Engineer Goal: Verify HAProxy / driver failover to mongos02 (port 27027) and recover mongos01.")

def heal_all():
    print("\n=== [HEAL & RESTORE] Bringing All 14 Cluster Containers Back Online ===")
    run_cmd("docker start csrs01 csrs02 csrs03 s1-node1 s1-node2 s1-node3 s2-node1 s2-node2 s2-node3 s3-node1 s3-node2 s3-node3 mongos01 mongos02", check=False)
    print("All containers started. Waiting 10 seconds for replica set catch-up...")
    time.sleep(10)
    print("Cluster restoration complete!")

def main():
    parser = argparse.ArgumentParser(description="MongoDB Sharded Cluster Chaos Engineering Tool")
    parser.add_argument("--scenario", type=int, choices=[1, 2, 3, 4, 5], help="Chaos Scenario ID to inject")
    parser.add_argument("--heal", action="store_true", help="Restore and start all cluster containers")
    
    args = parser.parse_args()
    
    if args.heal:
        heal_all()
        return

    if args.scenario == 1:
        chaos_scenario_1_primary_crash()
    elif args.scenario == 2:
        chaos_scenario_2_csrs_majority_loss()
    elif args.scenario == 3:
        chaos_scenario_3_oplog_rollover_burst()
    elif args.scenario == 4:
        chaos_scenario_4_jumbo_chunk_injection()
    elif args.scenario == 5:
        chaos_scenario_5_mongos_router_crash()
    else:
        print("MongoDB Chaos Generator - Select a scenario:")
        print("  1: Primary Node Crash (Shard 01)")
        print("  2: CSRS Majority Loss (Read-Only Metadata)")
        print("  3: Rapid Oplog Flooding (Change Stream Disruption)")
        print("  4: Jumbo Chunk Injection")
        print("  5: mongos Router Outage")
        print("  --heal: Restore all nodes")

if __name__ == "__main__":
    main()
