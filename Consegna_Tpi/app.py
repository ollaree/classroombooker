import os
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import pooling
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from dotenv import load_dotenv
import bcrypt

# Load environment
load_dotenv()
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'fallback_secret')
jwt = JWTManager(app)

# MySQL connection pool config
dbconfig = {
    "host": os.getenv('DB_HOST', 'localhost'),
    "user": os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD', ''),
    "database": os.getenv('DB_NAME', 'p_aule'),
    "pool_name": "mypool",
    "pool_size": 5,
    "autocommit": False
}
cnxpool = pooling.MySQLConnectionPool(**dbconfig)

def get_cursor():
    conn = cnxpool.get_connection()
    return conn, conn.cursor(dictionary=True)

def execute_query(query, params=None, fetch=False):
    conn, cursor = get_cursor()
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
        return result
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

@app.route('/', methods=['GET'])
def index():
    return jsonify({"msg": "hello"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        result = execute_query(
            "SELECT u.*, r.nome as ruolo FROM utente u "
            "JOIN ruoli r ON u.ruolo_id = r.id "
            "WHERE email = %s",
            (data['email'],),
            fetch=True
        )
        if not result:
            return jsonify({"msg": "Credenziali non valide"}), 401

        user = result[0]
        if not bcrypt.checkpw(data['password'].encode(), user['password'].encode()):
            return jsonify({"msg": "Credenziali non valide"}), 401

        access_token = create_access_token(
            identity=user['idUtente'],
            additional_claims={'role': user['ruolo']}
        )
        return jsonify(access_token=access_token)

    except mysql.connector.Error:
        return jsonify({"msg": "Errore nel database"}), 500

@app.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    data = request.get_json()
    try:
        conflict_check = """
            SELECT idPreno FROM prenotazione
            WHERE idAula = %s
            AND ((dataOraInizio < %s AND dataOraFine > %s)
            OR (dataOraInizio < %s AND dataOraFine > %s))
        """
        params = (
            data['idAula'],
            data['dataOraFine'], data['dataOraInizio'],
            data['dataOraInizio'], data['dataOraFine']
        )
        if execute_query(conflict_check, params, fetch=True):
            return jsonify({"msg": "Conflitto di orario rilevato"}), 400

        insert_query = """
            INSERT INTO prenotazione
            (idAula, idUtente, dataOraInizio, dataOraFine, motivazione)
            VALUES (%s, %s, %s, %s, %s)
        """
        execute_query(insert_query, (
            data['idAula'],
            user_id,
            datetime.fromisoformat(data['dataOraInizio']),
            datetime.fromisoformat(data['dataOraFine']),
            data.get('motivazione', '')
        ))
        return jsonify({"msg": "Prenotazione creata"}), 201

    except mysql.connector.Error:
        return jsonify({"msg": "Errore nel database"}), 500

@app.route('/calendario', methods=['GET'])
@jwt_required()
def calendario():
    try:
        query = """
            SELECT p.idPreno, p.idAula, p.idUtente, p.dataOraInizio, p.dataOraFine, p.motivazione, p.stato,
                   u.nome, u.cognome, u.email,
                   a.ubicazione, a.tipo
            FROM prenotazione p
            JOIN utente u ON p.idUtente = u.idUtente
            JOIN aula a ON p.idAula = a.idAula
            ORDER BY p.dataOraInizio
        """
        bookings = execute_query(query, fetch=True)
        calendario = {}
        for b in bookings:
            key = b['dataOraInizio'].strftime('%Y-%m-%d')
            calendario.setdefault(key, []).append({
                "idPreno": b["idPreno"],
                "idAula": b["idAula"],
                "idUtente": b["idUtente"],
                "dataOraInizio": b["dataOraInizio"].isoformat(),
                "dataOraFine": b["dataOraFine"].isoformat(),
                "motivazione": b["motivazione"],
                "stato": b["stato"],
                "utente": {"nome": b["nome"], "cognome": b["cognome"], "email": b["email"]},
                "aula": {"ubicazione": b["ubicazione"], "tipo": b["tipo"]}
            })
        return jsonify(calendario)
    except mysql.connector.Error:
        return jsonify({"msg": "Errore nel database"}), 500

@app.route('/report', methods=['GET'])
@jwt_required()
def report():
    try:
        query = """
            SELECT p.idAula, a.ubicazione, p.stato, COUNT(*) as totale
            FROM prenotazione p
            JOIN aula a ON p.idAula = a.idAula
            GROUP BY p.idAula, p.stato
            ORDER BY p.idAula
        """
        data = execute_query(query, fetch=True)
        return jsonify(data)
    except mysql.connector.Error:
        return jsonify({"msg": "Errore nel database"}), 500

if __name__ == '__main__':
    app.run(debug=True)
