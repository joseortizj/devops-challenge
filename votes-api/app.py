from flask import Flask, request, jsonify, g
from flask_cors import CORS
import psycopg2
import os
import socket
import random
import json

option_a = (
    os.getenv("OPTION_A")
    or (print("OPTION_A environment variable not set"), exit(1))[1]
)
option_b = (
    os.getenv("OPTION_B")
    or (print("OPTION_B environment variable not set"), exit(1))[1]
)
postgres_host = (
    os.getenv("POSTGRES_HOST")
    or (print("POSTGRES_HOST environment variable not set"), exit(1))[1]
)
postgres_user = (
    os.getenv("POSTGRES_USER")
    or (print("POSTGRES_USER environment variable not set"), exit(1))[1]
)
postgres_password = (
    os.getenv("POSTGRES_PASSWORD")
    or (print("POSTGRES_PASSWORD environment variable not set"), exit(1))[1]
)
postgres_db = (
    os.getenv("POSTGRES_DB")
    or (print("POSTGRES_DB environment variable not set"), exit(1))[1]
)
port = os.getenv("PORT") or (print("PORT environment variable not set"), exit(1))[1]

hostname = socket.gethostname()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def get_db():
    if not hasattr(g, "db"):
        try:
            g.db = psycopg2.connect(
                host=postgres_host,
                user=postgres_user,
                password=postgres_password,
                database=postgres_db,
            )
            # Create table if it doesn't exist
            cursor = g.db.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS votes (
                    id VARCHAR(255) NOT NULL UNIQUE,
                    vote VARCHAR(255) NOT NULL
                )
            """
            )
            g.db.commit()
            cursor.close()
        except psycopg2.Error as e:
            print(f"Database connection error: {e}", flush=True)
            g.db = None
    return g.db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "db") and g.db:
        g.db.close()


@app.route("/vote", methods=["POST"])
def vote_endpoint():
    """API endpoint to submit a vote"""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data or "vote" not in data:
            return jsonify({"error": "Missing vote data"}), 400

        vote = data["vote"]
        if vote not in ["a", "b"]:
            return jsonify({"error": "Invalid vote option. Must be 'a' or 'b'"}), 400

        # Get or generate voter ID
        voter_id = data.get("voter_id")
        if not voter_id:
            voter_id = hex(random.getrandbits(64))[2:-1]

        db = get_db()
        if not db:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            cursor = db.cursor()
            # Try to insert in the votes table, if voter already exists, update their vote
            cursor.execute(
                "INSERT INTO votes (id, vote) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET vote = EXCLUDED.vote",
                (voter_id, vote),
            )
            db.commit()
            cursor.close()

            return jsonify(
                {
                    "success": True,
                    "voter_id": voter_id,
                    "vote": vote,
                    "message": "Vote recorded successfully",
                }
            )
        except psycopg2.Error as e:
            print(f"Database error: {e}", flush=True)
            db.rollback()
            return jsonify({"error": f"Database error: {e}"}), 500

    except Exception as e:
        print(f"Unexpected error: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/", methods=["GET"])
def api_info():
    """API information endpoint with voting options"""
    return jsonify(
        {
            "service": "voting-api",
            "options": {"a": option_a, "b": option_b},
        }
    )


@app.route("/healthz", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok"})


@app.route("/results", methods=["GET"])
def results():
    """API endpoint to get voting results"""
    db = get_db()
    if not db:
        return json.dumps({"error": "Database connection failed"}), 500

    try:
        cursor = db.cursor()
        cursor.execute("SELECT vote, COUNT(id) AS count FROM votes GROUP BY vote")
        results = cursor.fetchall()
        cursor.close()

        # Convert results to the expected format
        votes = {"a": 0, "b": 0}
        for row in results:
            vote_option, count = row
            if vote_option in votes:
                votes[vote_option] = count

        return json.dumps(votes)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return json.dumps({"error": f"Database error: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
