# MongoDB Community Edition Sharded Cluster Operational Runbook & DR Guide

This document provides a production-grade operational manual, failure diagnosis guide, tuning handbook, monitoring/alerting specification, and local testing sandbox guide for engineering teams managing a **14-node MongoDB Community Edition** sharded cluster across Primary Data Center (DC) and Disaster Recovery Data Center (DR).

---

## 📄 Audience-Specific PDF Manuals & Downloadable ZIP Bundles

For targeted distribution across different operational roles, custom PDF manuals and complete code artifact ZIP archives have been generated:

| Role / Audience | Customized PDF Guide | Downloadable Code & Artifact ZIP Bundle | Package Contents |
| :--- | :--- | :--- | :--- |
| **Team Leader / Engineering Manager** | 📄 [mongodb_team_leader_guide.pdf](file:///home/vbg/.gemini/antigravity/brain/333d9d6b-b8bc-4b3e-a1a6-2f4068aade57/mongodb_team_leader_guide.pdf) | 📦 [team_leader_package.zip](file:///home/vbg/.gemini/antigravity/brain/333d9d6b-b8bc-4b3e-a1a6-2f4068aade57/team_leader_package.zip) | PDF Guide + Master Architecture Runbook & Governance Roadmap |
| **Engineering & Support Team** | 📄 [mongodb_engineer_field_manual.pdf](file:///home/vbg/.gemini/antigravity/brain/333d9d6b-b8bc-4b3e-a1a6-2f4068aade57/mongodb_engineer_field_manual.pdf) | 📦 [engineer_training_package.zip](file:///home/vbg/.gemini/antigravity/brain/333d9d6b-b8bc-4b3e-a1a6-2f4068aade57/engineer_training_package.zip) | PDF Field Manual + `docker-compose.yml` + `init_cluster.sh` + `mongodb_chaos_generator.py` + `rca_template.md` |
| **Site Reliability Engineer (SRE)** | 📄 [mongodb_sre_production_audit_guide.pdf](file:///home/vbg/.gemini/antigravity/brain/333d9d6b-b8bc-4b3e-a1a6-2f4068aade57/mongodb_sre_production_audit_guide.pdf) | 📦 [sre_production_audit_package.zip](file:///home/vbg/.gemini/antigravity/brain/333d9d6b-b8bc-4b3e-a1a6-2f4068aade57/sre_production_audit_package.zip) | PDF Audit Manual + `audit_mongodb.yml` + `mongodb_cluster_audit.py` + `prometheus.yml` + `alert.rules.yml` |

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

Production Prometheus scrape targets and Alertmanager rules (`alert.rules.yml`) cover replication lag (>10s / >60s), oplog window depletion (<6h), CSRS read-only state, `mongos` router drops, connection pool saturation (>80%), WiredTiger cache pressure (>85%), and PBM backup/PITR failures.

---

## 4. Operational Failure Domains & Detailed Runbooks

Covers CSRS quorum loss recovery, `mongos` router HA load balancing, WiredTiger cache pressure relief, PBM physical backup & PITR restoration, and jumbo chunk splits.

---

## 5. Automated Cluster Audit & Discovery Tooling

To ensure continuous compliance, SREs are provided with an automated discovery and audit script (`mongodb_cluster_audit.py`) and Ansible Playbook (`audit_mongodb.yml`) producing JSON (`mongodb_audit_report.json`) and HTML (`mongodb_audit_report.html`).

---

## 6. Local MongoDB DBA Testing Sandbox

Located in `/home/vbg/.gemini/antigravity/scratch/mongodb_cluster_setup`:
- `docker-compose.yml`: Spawns 14 MongoDB nodes + Prometheus + Grafana.
- `init_cluster.sh`: Automated multi-shard cluster setup.

---

## 7. Chaos Engineering Drills & Ticket RCA Guidelines

Engineers practice diagnosing and fixing injected failures using the **Chaos Engineering Suite** (`mongodb_chaos_generator.py`) and submit standardized RCA reports (`rca_template.md`).

---
> **Document Control**: Version 5.0 | Owner: Database Reliability & Infrastructure Team
