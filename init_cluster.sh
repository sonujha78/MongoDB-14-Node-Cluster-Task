#!/usr/bin/env bash
set -e

echo "================================================================="
echo "Initializing 14-Node MongoDB Sharded Cluster in Docker Sandbox..."
echo "================================================================="

# 1. Initialize Config Server Replica Set (CSRS)
echo "[1/5] Initiating Config Server Replica Set (csrs)..."
docker exec -i csrs01 mongosh --port 27019 --eval '
rs.initiate({
  _id: "csrs",
  configsvr: true,
  members: [
    { _id: 0, host: "csrs01:27019" },
    { _id: 1, host: "csrs02:27019" },
    { _id: 2, host: "csrs03:27019" }
  ]
})' || true

sleep 5

# 2. Initialize Shard 01
echo "[2/5] Initiating Shard 01 Replica Set (shard01)..."
docker exec -i s1-node1 mongosh --port 27018 --eval '
rs.initiate({
  _id: "shard01",
  members: [
    { _id: 0, host: "s1-node1:27018" },
    { _id: 1, host: "s1-node2:27018" },
    { _id: 2, host: "s1-node3:27018" }
  ]
})' || true

# 3. Initialize Shard 02
echo "[3/5] Initiating Shard 02 Replica Set (shard02)..."
docker exec -i s2-node1 mongosh --port 27018 --eval '
rs.initiate({
  _id: "shard02",
  members: [
    { _id: 0, host: "s2-node1:27018" },
    { _id: 1, host: "s2-node2:27018" },
    { _id: 2, host: "s2-node3:27018" }
  ]
})' || true

# 4. Initialize Shard 03
echo "[4/5] Initiating Shard 03 Replica Set (shard03)..."
docker exec -i s3-node1 mongosh --port 27018 --eval '
rs.initiate({
  _id: "shard03",
  members: [
    { _id: 0, host: "s3-node1:27018" },
    { _id: 1, host: "s3-node2:27018" },
    { _id: 2, host: "s3-node3:27018" }
  ]
})' || true

sleep 10

# 5. Add Shards to mongos Routers
echo "[5/5] Registering Shards with mongos Query Router..."
docker exec -i mongos01 mongosh --port 27017 --eval '
sh.addShard("shard01/s1-node1:27018,s1-node2:27018,s1-node3:27018");
sh.addShard("shard02/s2-node1:27018,s2-node2:27018,s2-node3:27018");
sh.addShard("shard03/s3-node1:27018,s3-node2:27018,s3-node3:27018");

// Enable sharding on reporting database and sample collection
sh.enableSharding("reporting_db");
sh.shardCollection("reporting_db.events", { customer_id: "hashed" });
' || true

echo "================================================================="
echo "Cluster initialization complete!"
echo "Mongos Router 1: mongodb://localhost:27017"
echo "Mongos Router 2: mongodb://localhost:27027"
echo "Prometheus UI:   http://localhost:9090"
echo "Grafana UI:      http://localhost:3000"
echo "================================================================="
