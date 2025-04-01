from flask import Blueprint, jsonify
import psycopg2
from config import DATABASE_URL
from flask import request

api = Blueprint("api", __name__)

# 首页
@api.route("/")
def home():
    return jsonify({"message": "Risk Monitoring API is running!"})

# 获取市场数据
@api.route("/api/market-data", methods=["GET"])
def get_market_data():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, timestamp, current_price FROM market_data")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    data = [
        {
            "symbol": row[0],
            "timestamp": row[1],
            "current_price": float(row[2])
        }
        for row in rows
    ]
    return jsonify(data)

# 获取客户持仓数据（带最新价格）
@api.route("/api/positions/<int:client_id>", methods=["GET"])
def get_positions(client_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # 使用最新一条市场价格数据
    cursor.execute("""
        SELECT p.symbol, p.quantity, p.cost_basis, md.current_price
        FROM positions p
        LEFT JOIN (
            SELECT DISTINCT ON (symbol) symbol, current_price
            FROM market_data
            ORDER BY symbol, timestamp DESC
        ) md ON p.symbol = md.symbol
        WHERE p.client_id = %s
    """, (client_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "symbol": row[0],
            "quantity": row[1],
            "cost_basis": float(row[2]),
            "current_price": float(row[3]) if row[3] is not None else None
        })

    return jsonify(result)

# 获取保证金状态
@api.route("/api/margin-status/<int:client_id>", methods=["GET"])
def get_margin_status(client_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # get position and current price
    cursor.execute("""
        SELECT p.symbol, p.quantity, md.current_price
        FROM positions p
        LEFT JOIN (
            SELECT DISTINCT ON (symbol) symbol, current_price
            FROM market_data
            ORDER BY symbol, timestamp DESC
        ) md ON p.symbol = md.symbol
        WHERE p.client_id = %s
    """, (client_id,))
    positions = cursor.fetchall()

    # get loan
    cursor.execute("SELECT loan FROM margin WHERE client_id = %s", (client_id,))
    loan_row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not loan_row:
        return jsonify({"error": "Loan data not found"}), 404
    loan = float(loan_row[0])

    # calculation logic
    portfolio_value = sum(float(qty) * float(price or 0) for _, qty, price in positions)
    net_equity = portfolio_value - loan
    margin_requirement = 0.25 * portfolio_value
    margin_shortfall = margin_requirement - net_equity
    margin_call = margin_shortfall > 0

    # update the margin requirement in the database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE margin
        SET margin_requirement = %s
        WHERE client_id = %s
    """, (margin_requirement, client_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "portfolio_value": round(portfolio_value, 2),
        "loan": round(loan, 2),
        "net_equity": round(net_equity, 2),
        "margin_requirement": round(margin_requirement, 2),
        "margin_shortfall": round(margin_shortfall, 2),
        "margin_call": margin_call
    })

# get all client_id
@api.route("/api/clients", methods=["GET"])
def get_all_clients():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT client_id FROM positions ORDER BY client_id;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    client_ids = [row[0] for row in rows]
    return jsonify(client_ids)

@api.route("/api/positions", methods=["POST"])
def create_position():
    data = request.get_json()
    required_fields = ["client_id", "symbol", "quantity", "cost_basis"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO positions (client_id, symbol, quantity, cost_basis)
            VALUES (%s, %s, %s, %s)
        """, (
            data["client_id"],
            data["symbol"].upper(),
            int(data["quantity"]),
            float(data["cost_basis"])
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Position added successfully"}), 201
    except Exception as e:
        print("Insert failed:", e)
        return jsonify({"error": "Database error"}), 500
