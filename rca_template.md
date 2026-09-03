# Incident Root Cause Analysis (RCA) & Resolution Report

**Ticket ID**: INC-XXXXX  
**Incident Title**: [Summary of Failure - e.g., Shard 01 Primary Failure / CSRS Read-Only State]  
**Severity**: [P1 - Critical / P2 - Major / P3 - Moderate]  
**Date & Time**: 2026-08-22 13:30:00 UTC  
**Impacted Environment**: Production 14-Node Sharded Cluster  

---

## 1. Executive Summary
Brief high-level description of what occurred, user/application impact, time to detect (TTD), and time to resolve (TTR).

- **Impact Start Time**: HH:MM UTC
- **Detection Time**: HH:MM UTC (via Prometheus Alert `MongoDBPrimaryNodeDown`)
- **Resolution Time**: HH:MM UTC
- **Total Downtime / Degradation**: XX Minutes
- **Data Loss / Uncommitted Writes**: 0 (RPO = 0 satisfied)

---

## 2. Technical Root Cause & Timeline
Detailed timeline of events leading up to the failure and technical explanation of the failure mode.

```
[HH:MM] - Chaos injection / hardware failure triggered on node s1-node1.
[HH:MM] - Prometheus alert fired: MongoDBPrimaryNodeDown.
[HH:MM] - On-call engineer investigated rs.status() on shard01 secondaries.
[HH:MM] - Election completed; s1-node2 elected as new PRIMARY.
[HH:MM] - s1-node1 restarted and rejoined set as SECONDARY.
```

### Root Cause Explanation
Explain *why* the failure happened (e.g., node process crash, quorum loss, oplog rollover, unindexed query storm).

---

## 3. Diagnostic Commands Executed
List the exact `mongosh` or CLI diagnostic commands used to investigate the incident.

```javascript
// 1. Checked Replica Set Health & Election State
rs.status();

// 2. Verified Cluster Shard Metadata & Balancer State
sh.status();

// 3. Checked Replication Lag & Oplog Window
db.printReplicationInfo();
```

---

## 4. Remediation Steps Taken
Document the step-by-step actions performed to restore service stability.

1. **Step 1**: Reconfigured replica set quorum / restarted node.
2. **Step 2**: Executed `replSetResizeOplog` to increase oplog retention.
3. **Step 3**: Flushed router metadata cache (`db.adminCommand({ flushRouterConfig: 1 })`).

---

## 5. Preventative & Corrective Action Items (CAPA)

| Action Item ID | Task Description | Owner | Target Date | Ticket Link |
| :--- | :--- | :--- | :--- | :--- |
| **CAPA-01** | Add Alertmanager notification channel for CSRS quorum degradation | SRE Team | 2026-08-25 | JIRA-101 |
| **CAPA-02** | Adjust `minRetentionHours: 48` across all shard nodes | DBA Team | 2026-08-23 | JIRA-102 |
| **CAPA-03** | Restrict chunk balancer window to 01:00-05:00 UTC | DBA Team | 2026-08-24 | JIRA-103 |

---
**Approved By**: Lead Database Reliability Engineer & Infrastructure Manager
