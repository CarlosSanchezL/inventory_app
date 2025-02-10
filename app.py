import json
from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime

app = Flask(__name__)
INVENTORY_FILE = "inventory.json"
HISTORY_FILE = "inventory_history.json"

# Cargar el inventario
try:
    with open(INVENTORY_FILE, "r") as file:
        inventory = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    inventory = {}

# Cargar el historial de inventario
def load_history():
    try:
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Guardar el inventario
def save_inventory():
    with open(INVENTORY_FILE, "w") as file:
        json.dump(inventory, file, indent=4)
    save_history()

# Guardar el historial diario
def save_history():
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    history[today] = inventory
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

@app.route('/')
def home():
    return render_template('index.html', inventory=inventory)

@app.route('/add', methods=['POST'])
def add_item():
    name = request.form.get("name", "").strip()
    quantity = request.form.get("quantity", "").strip()
    size = request.form.get("size", "").strip()
    
    if not name or not quantity or not size:
        return redirect(url_for('home'))
    
    try:
        quantity = int(quantity)
    except ValueError:
        return redirect(url_for('home'))
    
    item_key = f"{name} - {size}"
    
    if item_key in inventory:
        inventory[item_key]["quantity"] += quantity
    else:
        inventory[item_key] = {"quantity": quantity, "size": size}
    
    save_inventory()
    return redirect(url_for('home'))

@app.route('/delete', methods=['POST'])
def delete_item():
    item_key = request.form.get("name", "").strip()
    
    if item_key in inventory:
        del inventory[item_key]
        save_inventory()
    
    return redirect(url_for('home'))

@app.route('/update', methods=['POST'])
def update_item():
    item_key = request.form.get("name", "").strip()
    quantity = request.form.get("quantity", "").strip()
    
    if item_key in inventory and quantity.isdigit():
        inventory[item_key]["quantity"] = int(quantity)
        save_inventory()
    
    return redirect(url_for('home'))

@app.route('/list')
def list_inventory():
    return jsonify(inventory)

@app.route('/history')
def view_history():
    history = load_history()
    return jsonify(history)

@app.route('/reset', methods=['POST'])
def reset_inventory():
    global inventory
    save_history()  # Guarda el estado antes de borrar
    inventory = {}
    save_inventory()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
