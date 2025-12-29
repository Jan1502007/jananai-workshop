from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# -----------------------------
# In-memory DB
# -----------------------------
orders = {}

# -----------------------------
# Utility: calculate total
# -----------------------------
def calculate_total(items):
    return sum(i["price"] * i["qty"] for i in items)


# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    return jsonify({"message": "AI Billing System Running"})


# -----------------------------
# Create Order
# -----------------------------
@app.route("/create-order", methods=["POST"])
def create_order():
    data = request.json
    items = data.get("items", [])

    # validation
    for item in items:
        if item["qty"] <= 0 or item["price"] <= 0:
            return jsonify({"error": "Invalid price or quantity"}), 400

    order_id = str(int(time.time() * 1000))

    orders[order_id] = {
        "order_id": order_id,
        "items": items,
        "total": calculate_total(items),
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
# AI Agent – Smart Modify Bill
# -----------------------------
@app.route("/ai-agent", methods=["POST"])
def ai_agent():
    data = request.json
    order_id = data.get("order_id")
    action = data.get("action")  # add / remove / increment / decrement
    item = data.get("item")

    if order_id not in orders:
        return jsonify({"error": "Order not found"}), 404

    order = orders[order_id]
    items = order["items"]

    # find item
    existing = next((i for i in items if i["name"] == item["name"]), None)

    if action == "add":
        if existing:
            existing["qty"] += item["qty"]
        else:
            items.append(item)

    elif action == "increment" and existing:
        existing["qty"] += 1

    elif action == "decrement" and existing:
        existing["qty"] -= 1
        if existing["qty"] <= 0:
            items.remove(existing)

    elif action == "remove" and existing:
        items.remove(existing)

    else:
        return jsonify({"error": "Invalid action or item"}), 400

    # recalc total
    order["total"] = calculate_total(items)

    return jsonify({
        "message": "Order updated successfully",
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
# Run
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
