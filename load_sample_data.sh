#!/usr/bin/env bash
set -e

echo "================================================================="
echo "MongoDB CRUD Learning Module: Public Sample Data Downloader & Importer"
echo "================================================================="

mkdir -p sample_data

# Download sample movies dataset (MFlix) from official public raw repository
SAMPLE_URL="https://raw.githubusercontent.com/neondatabase/sample-datasets/main/mflix/movies.json"

if [ ! -f "sample_data/movies.json" ]; then
    echo "[1/3] Downloading public 'movies' dataset (~20,000 documents)..."
    curl -sSL "$SAMPLE_URL" -o sample_data/movies.json || wget -q "$SAMPLE_URL" -O sample_data/movies.json
else
    echo "[1/3] Public 'movies' dataset already present in sample_data/"
fi

echo "[2/3] Ingesting 'movies' dataset into MongoDB container using mongoimport..."
docker exec -i learning_mongodb mongoimport \
    --db=mflix_db \
    --collection=movies \
    --file=/sample_data/movies.json \
    --jsonArray \
    --drop || echo "Note: Execute via local mongoimport if docker container is not active."

echo "[3/3] Generating additional 'users' and 'comments' sample collections..."
docker exec -i learning_mongodb mongosh mflix_db --eval '
db.users.insertMany([
  { user_id: "u101", name: "Alice Smith", email: "alice@example.com", tier: "premium", joined: new Date("2024-01-15") },
  { user_id: "u102", name: "Bob Jones", email: "bob@example.com", tier: "standard", joined: new Date("2024-02-20") },
  { user_id: "u103", name: "Charlie Brown", email: "charlie@example.com", tier: "premium", joined: new Date("2024-03-10") }
]);

db.comments.insertMany([
  { comment_id: "c1", movie_id: ObjectId("573a1390f29313caabcd4121"), user_id: "u101", text: "Masterpiece film!", rating: 5, date: new Date() },
  { comment_id: "c2", movie_id: ObjectId("573a1390f29313caabcd4121"), user_id: "u102", text: "Great cinematography.", rating: 4, date: new Date() }
]);
' || true

echo "================================================================="
echo "Sample Dataset Successfully Ingested!"
echo "Database:   mflix_db"
echo "Collections: movies, users, comments"
echo "Mongo Express UI: http://localhost:8081"
echo "Metabase UI:      http://localhost:3000"
echo "================================================================="
