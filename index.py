from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# -----------------------------
# In-memory order storage
# -----------------------------
orders = {}

# -----------------------------
# Home route
# -----------------------------
@app.route("/")
def home():
    return jsonify({"message": "AI Billing System Backend Running"})


# -----------------------------
# Create Order
# -----------------------------
@app.route("/create-order", methods=["POST"])
def create_order():
    data = request.json
    items = data.get("items", [])

    total = sum(item["price"] * item["qty"] for item in items)

    order_id = str(int(time.time() * 1000))  # unique id

    orders[order_id] = {
        "order_id": order_id,
        "items": items,
        "total": total,
        "status": "PENDING"
    }

    return jsonify(orders[order_id])


# -----------------------------
# Get Order
# -----------------------------
@app.route("/order/<order_id>", methods=["GET"])
def get_order(order_id):
    if order_id not in orders:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(orders[order_id])


# -----------------------------
# AI Agent – Modify Bill
# -----------------------------
@app.route("/ai-agent", methods=["POST"])
def ai_agent():
    data = request.json
    order_id = data.get("order_id")
    action = data.get("action")  # add / remove
    item = data.get("item")

    if order_id not in orders:
        return jsonify({"error": "Order not found"}), 404

    order = orders[order_id]

    if action == "add":
        order["items"].append(item)

    elif action == "remove":
        order["items"] = [
            i for i in order["items"] if i["name"] != item["name"]
        ]

    # Recalculate total
    order["total"] = sum(i["price"] * i["qty"] for i in order["items"])

    return jsonify({
        "message": "Order updated by AI agent",
        "order": order
    })


# -----------------------------
# Complete Order
# -----------------------------
@app.route("/complete-order/<order_id>", methods=["POST"])
def complete_order(order_id):
    if order_id not in orders:
        return jsonify({"error": "Order not found"}), 404

    orders[order_id]["status"] = "COMPLETED"
    return jsonify(orders[order_id])


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
