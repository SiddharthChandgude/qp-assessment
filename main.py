from flask import Flask, render_template, request, redirect, session, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="abc123",
    database="grocery_db",
    cursorclass=pymysql.cursors.DictCursor
)

# Test admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"

# Index page
@app.route('/')
def index():
    return render_template('index.html')

# Admin login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect('/admin_dashboard')
        else:
            flash('Invalid username or password', 'error')
    return render_template('admin_login.html')

# Admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect('/admin_login')  # Redirect to login if not logged in
    return render_template('admin_dashboard.html')

# Add new grocery item
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        inventory = int(request.form['inventory'])
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO grocery_items (name, price, inventory) VALUES (%s, %s, %s)", (name, price, inventory))
            conn.commit()
            cursor.close()
            flash('Item added successfully', 'success')
            return redirect('/add_item')
        except pymysql.Error as e:
            flash('Error: {}'.format(e), 'error')
    return render_template('add_item.html')

# Remove grocery item
@app.route('/remove_item', methods=['GET', 'POST'])
def remove_item():
    if request.method == 'POST':
        item_id = request.form['item_id']
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM grocery_items WHERE id = %s", (item_id,))
            conn.commit()
            cursor.close()
            flash('Item removed successfully', 'success')
            return redirect('/remove_item')
        except pymysql.Error as e:
            flash('Error: {}'.format(e), 'error')
    return render_template('remove_item.html')

# Update grocery item
@app.route('/update_item', methods=['GET', 'POST'])
def update_item():
    if request.method == 'POST':
        item_id = request.form['item_id']
        name = request.form.get('name')
        price = request.form.get('price')
        inventory = request.form.get('inventory')

        try:
            cursor = conn.cursor()
            if name:
                cursor.execute("UPDATE grocery_items SET name = %s WHERE id = %s", (name, item_id))
            if price:
                cursor.execute("UPDATE grocery_items SET price = %s WHERE id = %s", (price, item_id))
            if inventory:
                cursor.execute("UPDATE grocery_items SET inventory = %s WHERE id = %s", (inventory, item_id))
            conn.commit()
            cursor.close()
            flash('Item updated successfully', 'success')
            return redirect('/update_item')
        except pymysql.Error as e:
            flash('Error: {}'.format(e), 'error')
    return render_template('update_item.html')

# View grocery items for user
@app.route('/view_items_user')
def view_items_user():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM grocery_items")
    items = cursor.fetchall()
    cursor.close()
    return render_template('view_items_user.html', items=items)

# Add item to basket for user
@app.route('/add_to_basket', methods=['POST'])
def add_to_basket():
    item_id = int(request.form['id'])
    item_name = request.form['name']
    item_price = float(request.form['price'])
    quantity = int(request.form['quantity'])  # Retrieve selected quantity

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO temporary_basket (item_id, name, price, quantity) VALUES (%s, %s, %s, %s)", (item_id, item_name, item_price, quantity))
        conn.commit()
        cursor.close()

        flash('Item added to basket', 'success')
    except pymysql.Error as e:
        flash('Error: {}'.format(e), 'error')

    return redirect('/view_items_user')

@app.route('/basket')
def basket():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temporary_basket")
    basket_items = cursor.fetchall()
    cursor.close()

    total_price = sum(item['price'] * item['quantity'] for item in basket_items)
    return render_template('basket.html', basket=basket_items, total_price=total_price)


# Delete item from basket
@app.route('/delete_from_basket', methods=['POST'])
def delete_from_basket():
    item_id = request.form['item_id']
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM temporary_basket WHERE item_id = %s", (item_id,))
        conn.commit()
        cursor.close()
        flash('Item removed from basket', 'success')
    except pymysql.Error as e:
        flash('Error: {}'.format(e), 'error')

    return redirect('/basket')

# Confirm booking
@app.route('/confirm_booking')
def confirm_booking():
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO permanent_basket SELECT * FROM temporary_basket")
        cursor.execute("TRUNCATE TABLE temporary_basket")
        conn.commit()
        cursor.close()
        flash('Booking confirmed!', 'success')
    except pymysql.Error as e:
        flash('Error: {}'.format(e), 'error')

    return redirect('/view_items_user')

if __name__ == "__main__":
    app.run(debug=True)
