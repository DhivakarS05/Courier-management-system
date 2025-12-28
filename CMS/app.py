from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from reportlab.pdfgen import canvas
import io
import smtplib
import os
import random, string

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ================= DATABASE CONNECTION =================

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="courier_user",
        password="CourierPass123!",
        database="courier_db"
    )

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("home.html")
# =========================================================================================== LOGIN =========================================================================================

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None  # store validation messages

    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        phone = request.form.get("phone").strip()
        role = "customer"

        # ---------------- VALIDATIONS ----------------
        import re

        if not username:
            error = "Username is required."
        elif not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
            error = "Please enter a valid Gmail address ending with @gmail.com."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        elif not phone.isdigit() or len(phone) != 10:
            error = "Enter a valid 10-digit phone number."

        if error:
            return render_template("register.html", error=error, username=username, email=email, phone=phone)

        # ---------------- DATABASE CHECK ----------------
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
            existing_user = cursor.fetchone()
            if existing_user:
                error = "Username or Email already exists."
                return render_template("register.html", error=error, username=username, email=email, phone=phone)

            cursor.execute(
                "INSERT INTO users (username, email, password, phone, role) VALUES (%s, %s, %s, %s, %s)",
                (username, email, password, phone, role)
            )
            conn.commit()
            flash("Registered successfully!", "success")
            return redirect(url_for("login_user"))

        except Exception as e:
            error = f"Database error: {str(e)}"
            return render_template("register.html", error=error, username=username, email=email, phone=phone)

        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")

# ---------- USER LOGIN ----------
@app.route("/login_user", methods=["GET","POST"])
def login_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["role"] = "customer"
            return redirect(url_for("customer_dashboard"))
        else:
            flash("Invalid Customer Credentials!", "error")

    return render_template("login_user.html")

# ---------- ADMIN LOGIN ----------
@app.route("/login_admin", methods=["GET","POST"])
def login_admin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin:
            session["user_id"] = admin["id"]
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            # Flash message for invalid credentials
            flash("Invalid username or password. Please try again.", "danger")
            return render_template("login_admin.html")

    return render_template("login_admin.html")

# ---------- STAFF LOGIN ----------
@app.route("/login_staff", methods=["GET", "POST"])
def login_staff():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM staff WHERE username=%s AND password=%s", (username, password))
        staff = cursor.fetchone()
        cursor.close()
        conn.close()

        if staff:
            session["user_id"] = staff["id"]
            session["role"] = "staff"
            flash("Login successful!", "success")
            return redirect(url_for("staff_dashboard"))
        else:
            flash("Incorrect username or password!", "error")
            # Stay on the same page

    return render_template("login_staff.html")


# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

# ================= CUSTOMER DASHBOARD =================
@app.route('/customer_dashboard')
def customer_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login first.", "danger")
        return redirect(url_for("login_user"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM couriers WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    couriers = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("customer_dashboard.html", couriers=couriers)

# ========================= ADMIN DASHBOARD ========================
@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login_admin"))
    return render_template("admin_dashboard.html")


# ---------- VIEW STAFF ----------
@app.route("/admin/staff")
def view_staff():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM staff")
    staff = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("view_staff.html", staff=staff)


# ---------- ADD STAFF ----------
@app.route("/admin/staff/add", methods=["GET", "POST"])
def add_staff():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # check if username already exists
        cursor.execute("SELECT id FROM staff WHERE username = %s", (username,))
        existing = cursor.fetchone()

        if existing:
            flash("Username already exists. Please choose another.", "error")
        else:
            cursor.execute(
                "INSERT INTO staff (name, username, password) VALUES (%s, %s, %s)",
                (name, username, password),
            )
            conn.commit()
            flash("Staff Added Successfully!", "success")

        cursor.close()
        conn.close()
        return redirect(url_for("view_staff"))

    return render_template("add_staff.html")



# ---------- EDIT STAFF ----------
@app.route("/admin/staff/edit/<int:staff_id>", methods=["GET", "POST"])
def edit_staff(staff_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("UPDATE staff SET name=%s, username=%s, password=%s WHERE id=%s", 
                       (name, username, password, staff_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Staff Updated Successfully!", "success")
        return redirect(url_for("view_staff"))

    cursor.execute("SELECT * FROM staff WHERE id=%s", (staff_id,))
    staff = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("edit_staff.html", staff=staff)


# ---------- DELETE STAFF ----------
@app.route("/admin/staff/delete/<int:staff_id>")
def delete_staff(staff_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM staff WHERE id=%s", (staff_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Staff Deleted Successfully!", "success")
    return redirect(url_for("view_staff"))

# ---------- ASSIGN STAFF ----------
@app.route("/assign_staff", methods=["GET", "POST"])
def assign_staff_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        courier_id = request.form.get("courier_id")
        staff_id = request.form.get("staff_id")
        try:
            cursor.execute(
                "UPDATE couriers SET staff_id = %s WHERE id = %s",
                (staff_id, courier_id)
            )
            conn.commit()
            flash("Staff assigned successfully!", "success")
        except mysql.connector.Error as e:
            conn.rollback()
            flash(f"Database Error (assign staff): {str(e)}", "danger")
        return redirect(url_for("assign_staff_page"))

    # Fetch all couriers
    couriers = []
    try:
        cursor.execute("""
            SELECT c.id AS courier_id,
                   c.sender_name, c.sender_phone,
                   c.receiver_name, c.receiver_phone,
                   c.sender_address AS pickup_address,
                   c.receiver_address AS delivery_address,
                   c.status,
                   s.name AS staff_name
            FROM couriers c
            LEFT JOIN staff s ON c.staff_id = s.id
            ORDER BY c.id DESC
        """)
        couriers = cursor.fetchall()
        print("DEBUG couriers:", couriers)
    except mysql.connector.Error as e:
        flash(f"Database Error (fetch couriers): {str(e)}", "danger")

    # Fetch all staff
    staff_list = []
    try:
        cursor.execute("SELECT id AS staff_id, name FROM staff")
        staff_list = cursor.fetchall()
        print("DEBUG staff_list:", staff_list)
    except mysql.connector.Error as e:
        flash(f"Database Error (fetch staff): {str(e)}", "danger")

    cursor.close()
    conn.close()

    return render_template("assign_staff.html", couriers=couriers, staff_list=staff_list)



# ---------- VIEW CUSTOMERS ----------
@app.route("/admin/customers")
def view_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("view_customers.html", customers=customers)


# ---------- VIEW COURIERS ----------
@app.route("/admin/couriers")
def view_couriers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM couriers")
    couriers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("view_couriers.html", couriers=couriers)


# ---------- VIEW TRACKING IDS ----------
@app.route("/admin/tracking")
def view_tracking():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, tracking_id FROM couriers")
    tracking = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("view_tracking.html", tracking=tracking)


# ================= STAFF DASHBOARD =================
@app.route("/staff")
def staff_dashboard():
    if session.get("role") != "staff":
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.id, c.tracking_id, c.sender_name, c.sender_phone, c.sender_address,
               c.receiver_name, c.receiver_phone, c.receiver_address, 
               c.courier_type, c.weight, c.total_cost, 
               c.status, c.created_at,
               u.username AS customer_name, u.email AS customer_email, u.phone AS customer_phone
        FROM couriers c
        JOIN users u ON c.user_id = u.id
        WHERE c.staff_id = %s
        ORDER BY c.created_at DESC
    """, (session["user_id"],))

    couriers = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("staff_dashboard.html", couriers=couriers)

@app.route("/update_status/<int:courier_id>", methods=["GET","POST"])
def update_status(courier_id):
    new_status = request.form["status"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE couriers SET status=%s WHERE id=%s", (new_status, courier_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Status updated successfully!", "success")
    return redirect(url_for("staff_dashboard"))

# ===========================================================================================  Book Courier Page  =========================================================================================

# Generate random tracking ID
def generate_tracking_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ----------------- Book Courier Page -----------------
@app.route("/book_courier", methods=["GET", "POST"])
def book_courier():
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to book a courier.", "danger")
        return redirect(url_for("login_user"))

    if request.method == "POST":
        # Collect form data
        sender_name = request.form["sender_name"]
        sender_address = request.form["pickup_address"]
        sender_pincode = request.form["sender_pincode"]
        sender_phone = request.form["sender_phone"]

        receiver_name = request.form["receiver_name"]
        receiver_address = request.form["receiver_address"]
        receiver_pincode = request.form["receiver_pincode"]
        receiver_phone = request.form["receiver_phone"]

        courier_type = request.form.get("courier_type")
        try:
            weight = float(request.form.get("weight", 0))
        except ValueError:
            flash("Weight must be a number.", "danger")
            return render_template("book_courier.html")

        pickup = request.form.get("pickup") == "on"
        insurance = request.form.get("insurance") == "on"

        # Server-side validation
        if not sender_pincode.isdigit() or len(sender_pincode) != 6:
            flash("Sender pincode must be 6 digits.", "danger")
            return render_template("book_courier.html")

        if not receiver_pincode.isdigit() or len(receiver_pincode) != 6:
            flash("Receiver pincode must be 6 digits.", "danger")
            return render_template("book_courier.html")

        if not sender_phone.isdigit() or len(sender_phone) != 10:
            flash("Sender phone must be 10 digits.", "danger")
            return render_template("book_courier.html")

        if not receiver_phone.isdigit() or len(receiver_phone) != 10:
            flash("Receiver phone must be 10 digits.", "danger")
            return render_template("book_courier.html")

        # Calculate cost
        base_cost = weight * (30 if courier_type == "normal" else 50)
        if weight < 0.5:
            base_cost = 50  # minimum charge
        pickup_charge = 50 if pickup else 0
        insurance_charge = round(base_cost * 0.02, 2) if insurance else 0
        total_cost = round(base_cost + pickup_charge + insurance_charge, 2)

        # Save data in session for preview
        session["preview"] = {
            "sender_name": sender_name,
            "sender_address": sender_address,
            "sender_pincode": sender_pincode,
            "sender_phone": sender_phone,
            "receiver_name": receiver_name,
            "receiver_address": receiver_address,
            "receiver_pincode": receiver_pincode,
            "receiver_phone": receiver_phone,
            "courier_type": courier_type,
            "weight": weight,
            "pickup_charge": pickup_charge,
            "insurance_charge": insurance_charge,
            "total_cost": total_cost
        }

        return redirect(url_for("preview_courier"))

    return render_template("book_courier.html")
# ---------------- preview courier details  ----------------

@app.route("/preview_courier", methods=["GET", "POST"])
def preview_courier():
    preview = session.get("preview")
    if not preview:
        flash("No courier data to preview.", "danger")
        return redirect(url_for("book_courier"))

    if request.method == "POST":
        user_id = session.get("user_id")
        tracking_id = generate_tracking_id()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO couriers
            (user_id, sender_name, sender_address, sender_pincode, sender_phone,
             receiver_name, receiver_address, receiver_pincode, receiver_phone,
             tracking_id, courier_type, weight, pickup_charge, insurance_charge, total_cost)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            preview["sender_name"],
            preview["sender_address"],
            preview["sender_pincode"],
            preview["sender_phone"],
            preview["receiver_name"],
            preview["receiver_address"],
            preview["receiver_pincode"],
            preview["receiver_phone"],
            tracking_id,
            preview["courier_type"],
            preview["weight"],
            preview["pickup_charge"],
            preview["insurance_charge"],
            preview["total_cost"]
        ))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Courier booked successfully! Tracking ID: {tracking_id}", "success")
        session.pop("preview")
        return redirect(url_for("customer_dashboard"))

    return render_template("preview_courier.html", preview=preview)

# ----------------- My Couriers -----------------
@app.route("/my_couriers")
def my_couriers():
    if session.get("role") != "customer":
        return redirect(url_for("customer_dashboard"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM couriers WHERE user_id=%s ORDER BY id DESC", (session["user_id"],))
    couriers = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("my_couriers.html", couriers=couriers)

@app.route("/courier/<tracking_id>")
def courier_details(tracking_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM couriers WHERE tracking_id=%s", (tracking_id,))
    courier = cursor.fetchone()
    cursor.close()
    conn.close()

    if not courier:
        flash("Courier not found.", "danger")
        return redirect(url_for("my_couriers"))

    return render_template("courier_details.html", courier=courier)

# ---------------- Cancel Courier ----------------
@app.route("/cancel/<int:courier_id>")
def cancel_courier(courier_id):
    if session.get("role") != "customer":
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM couriers WHERE id=%s AND user_id=%s", (courier_id, session["user_id"]))
    courier = cursor.fetchone()

    if courier and courier["status"] == "Booked":
        cursor.execute("DELETE FROM couriers WHERE id=%s", (courier_id,))
        conn.commit()

        cursor.execute("SELECT email FROM users WHERE id=%s", (session["user_id"],))
        cust = cursor.fetchone()
        send_email(cust["email"], "Courier Cancelled",
                   f"Your courier with ID {courier_id} has been cancelled successfully.")

        cursor.close()
        conn.close()
        return redirect(url_for("my_couriers"))
    else:
        cursor.close()
        conn.close()
        return "Cannot cancel this courier (already assigned or delivered)."

# ---------------- Track Courier ----------------

@app.route('/track', methods=['GET', 'POST'])
def track_courier():
    courier = None
    if request.method == 'POST':
        tracking_id = request.form.get('tracking_id')
        if not tracking_id:
            flash("Please enter a tracking ID.", "warning")
        else:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM couriers WHERE tracking_id=%s", (tracking_id,))
            courier = cursor.fetchone()
            cursor.close()
            conn.close()

            if not courier:
                flash("Tracking ID not found.", "danger")

    return render_template('track_courier.html', courier=courier)


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ================= RUN =================
if __name__=="__main__":
    app.run(debug=True)
