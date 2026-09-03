# MongoDB Community Edition Sharded Cluster Operational Runbook & DR Guide

This document provides a production-grade operational manual, failure diagnosis guide, tuning handbook, monitoring/alerting specification, and local testing sandbox guide for engineering teams managing a **14-node MongoDB Community Edition** sharded cluster across Primary Data Center (DC) and Disaster Recovery Data Center (DR).

---

## 1. Architecture & Topology Blueprint (14 Nodes in Primary DC)

### 1.1 Detailed Node Distribution

- **Shard 01 (`shard01`)**: 3 Replicas (`s1-node1` [Primary], `s1-node2` [Secondary], `s1-node3` [Secondary])
- **Shard 02 (`shard02`)**: 3 Replicas (`s2-node1` [Primary], `s2-node2` [Secondary], `s2-node3` [Secondary])
- **Shard 03 (`shard03`)**: 3 Replicas (`s3-node1` [Primary], `s3-node2` [Secondary], `s3-node3` [Secondary])
- **Config Server Replica Set (CSRS)**: 3 Config Nodes (`csrs01` [Primary], `csrs02` [Secondary], `csrs03` [Secondary])
- **Query Routers**: 2 `mongos` router nodes (`mongos01`, `mongos02`)
- **Total Primary DC Nodes**: **14 Nodes** (9 Data Nodes + 3 Config Nodes + 2 Routers)

```
                                  +-----------------------------+
                                  |     Application Clients     |
                                  +-----------------------------+
                                                 |
                                                 v
                                    +--------------------------+
                                    | Load Balancer (VIP / L7) |
                                    +--------------------------+
                                       /                    \
                                      v                      v
                               +--------------+       +--------------+
                               |   mongos01   |       |   mongos02   |  (Routers)
                               +--------------+       +--------------+
                                      |                      |
            +-------------------------+----------------------+-------------------------+
            |                         |                      |                         |
            v                         v                      v                         v
  +-------------------+     +-------------------+  +-------------------+     +-------------------+
  | Config RS (CSRS)  |     | Shard 01 (3-node) |  | Shard 02 (3-node) |     | Shard 03 (3-node) |
  | csrs01, 02, 03    |     | s1-n1, n2, n3     |  | s2-n1, n2, n3     |     | s3-n1, n2, n3     |
  +-------------------+     +-------------------+  +-------------------+     +-------------------+
```

---

## 2. DC-DR Topology & Failover Design

### 2.1 Stretched Cluster Strategy (Active-Passive DR)

Add a **4th hidden, non-voting member** in the DR Data Center for each replica set (3 Shards + CSRS):
- **Primary DC**: 3 Nodes per Shard (`priority: 1, votes: 1`) + 3 CSRS Nodes (`priority: 1, votes: 1`).
- **DR DC**: 1 Hidden Node per Shard (`priority: 0, votes: 0, hidden: true`) + 1 CSRS Node (`priority: 0, votes: 0, hidden: true`) + 2 Standby `mongos` Routers.

---

## 3. Monitoring, Alerting & Observability Framework

### 3.1 Prometheus Metrics Scraping with `mongodb_exporter`
Scrape configuration and production alert rules (`alert.rules.yml`) cover replication lag (>10s / >60s), oplog window depletion (<6h), CSRS read-only state, `mongos` router drops, connection pool saturation (>80%), WiredTiger cache pressure (>85%), and PBM backup/PITR failures.

---

## 4. Operational Failure Domains & Detailed Runbooks

Covers CSRS quorum loss recovery, `mongos` router HA load balancing, WiredTiger cache pressure relief, PBM physical backup & PITR restoration, and jumbo chunk splits.

---

## 5. Automated Cluster Audit & Discovery Tooling

To ensure continuous compliance, the team is provided with an automated discovery and audit script (`mongodb_cluster_audit.py`) and Ansible Playbook (`audit_mongodb.yml`) producing JSON (`mongodb_audit_report.json`) and HTML (`mongodb_audit_report.html`).

---

## 6. Local MongoDB DBA Testing Sandbox

Located in `/home/vbg/.gemini/antigravity/scratch/mongodb_cluster_setup`:
- `docker-compose.yml`: Spawns 14 MongoDB nodes + Prometheus + Grafana.
- `init_cluster.sh`: Automated multi-shard cluster setup.

---

## 7. Chaos Engineering Drills & Ticket RCA Guidelines

To build operational readiness, engineers practice diagnosing and fixing injected failures using the **Chaos Engineering Suite** in `/home/vbg/.gemini/antigravity/scratch/mongodb_cluster_setup/mongodb_chaos_generator.py`.

### 7.1 Chaos Injection CLI Commands

```bash
# Inject Scenario 1: Primary Node Crash (Shard 01)
python3 mongodb_chaos_generator.py --scenario 1

# Inject Scenario 2: Config Server Replica Set Majority Loss (Metadata Read-Only)
python3 mongodb_chaos_generator.py --scenario 2

# Inject Scenario 3: Oplog Rollover Burst (Change Stream Disruption)
python3 mongodb_chaos_generator.py --scenario 3

# Inject Scenario 4: Jumbo Chunk Generation & Balancer Stall
python3 mongodb_chaos_generator.py --scenario 4

# Inject Scenario 5: mongos Router Failure
python3 mongodb_chaos_generator.py --scenario 5

# Heal & Restore Cluster to Clean State
python3 mongodb_chaos_generator.py --heal
```

---

### 7.2 Ticket RCA & Resolution Submission Protocol

For every chaos drill or real incident, engineers must complete and post the **RCA & Resolution Template** ([rca_template.md](file:///home/vbg/.gemini/antigravity/scratch/mongodb_cluster_setup/rca_template.md)) to the team ticketing system (Jira / ServiceNow):

#### Mandatory Ticket Requirements:
1. **Time to Detect (TTD) & Time to Resolve (TTR)** metrics.
2. **Prometheus Alert Triggered** (e.g., `MongoDBPrimaryNodeDown`, `MongoDBConfigServerQuorumDegraded`).
3. **Exact `mongosh` Diagnostic Commands Executed** (`rs.status()`, `sh.status()`, `db.printReplicationInfo()`).
4. **Step-by-Step Remediation Actions**.
5. **Preventative Action Items (CAPA)** with assigned owner and target date.

---
> **Document Control**: Version 4.0 | Owner: Database Reliability & Infrastructure Team
