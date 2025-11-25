from flask import Flask, jsonify, request
import time, requests, os
from jose import jwt
import json
import mysql.connector
import logging

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Cấu hình OAuth2
ISSUER = os.getenv("OIDC_ISSUER", "http://localhost:8081/realms/realm_sv001")  # Issuer cho validation, khớp token
JWKS_URL = os.getenv("OIDC_JWKS_URL", "http://authentication-identity-server:8080/realms/realm_sv001/protocol/openid-connect/certs")  # JWKS dùng internal URL
AUDIENCE = os.getenv("OIDC_AUDIENCE", "account")

# Cấu hình MariaDB
DB_CONFIG = {
    'host': 'relational-database-server',
    'user': 'root',
    'password': 'root',
    'port': 3306
}

_JWKS = None; _TS = 0

def get_jwks():
    global _JWKS, _TS
    now = time.time()
    if not _JWKS or now - _TS > 600:
        try:
            logging.debug(f"Fetching JWKS from: {JWKS_URL}")
            response = requests.get(JWKS_URL, timeout=5)
            logging.debug(f"Response status: {response.status_code}")
            logging.debug(f"Response text: {response.text}")
            _JWKS = response.json()
        except Exception as e:
            logging.error(f"Failed to fetch JWKS: {e}")
            raise
        _TS = now
    return _JWKS

def get_db_connection(database='studentdb'):
    """Kết nối đến MariaDB database"""
    try:
        config = DB_CONFIG.copy()
        config['database'] = database
        conn = mysql.connector.connect(**config)
        logging.info(f"Connected to MariaDB database: {database}")
        return conn
    except Exception as e:
        logging.error(f"MariaDB connection error: {e}")
        return None

app = Flask(__name__)

@app.get("/hello")
def hello(): 
    return jsonify(message="Hello from App Server!")

@app.get("/secure")
def secure():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "):
        return jsonify(error="Missing Bearer token"), 401
    token = auth.split(" ",1)[1]
    try:
        payload = jwt.decode(token, get_jwks(), algorithms=["RS256"], audience=AUDIENCE, issuer=ISSUER)
        return jsonify(message="Secure resource OK", preferred_username=payload.get("preferred_username"))
    except Exception as e:
        return jsonify(error=str(e)), 401

@app.get("/student")
def student():
    try:
        with open("students.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        logging.debug(f"Loaded students: {data}")
        return jsonify(data)
    except Exception as e:
        logging.exception("Cannot read students.json")
        return jsonify(error=str(e)), 500

# ========== ENDPOINT MỚI ĐỌC DỮ LIỆU TỪ MARIADB ==========

@app.get("/api/students")
def get_students_from_db():
    """Lấy danh sách students từ MariaDB database"""
    try:
        conn = get_db_connection('studentdb')
        if not conn:
            return jsonify(error="Cannot connect to MariaDB"), 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        
        logging.debug(f"Loaded {len(students)} students from MariaDB")
        return jsonify({
            'source': 'MariaDB',
            'count': len(students),
            'students': students
        })
    except Exception as e:
        logging.exception("Error fetching students from MariaDB")
        return jsonify(error=str(e)), 500

@app.get("/health/db")
def health_check():
    """Kiểm tra kết nối database"""
    try:
        conn = get_db_connection('studentdb')
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()  # THÊM DÒNG NÀY
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'healthy',
                'database': 'MariaDB',
                'message': 'Database connection successful',
                'test_result': result[0]  # THÊM DÒNG NÀY
            })
        else:
            return jsonify({
                'status': 'unhealthy', 
                'database': 'MariaDB',
                'message': 'Cannot connect to database'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'MariaDB',
            'error': str(e)
        }), 500

if __name__ == "__main__":
    logging.info("Starting Flask app...")
    app.run(host="0.0.0.0", port=8081, debug=True)
