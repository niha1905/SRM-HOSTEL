from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash
from flask_mysqldb import MySQL
import qrcode
import io
import base64
from flask import url_for


app = Flask(__name__)
app.secret_key = '123'


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Niyuk1905!',
    'database': 'srm_hostel_management'
}


def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


@app.route('/')
def home():
    today = datetime.now().strftime("%A")
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    
    cursor.execute("SELECT * FROM weekly_menu WHERE day = %s", (today,))
    meals = cursor.fetchall()

    total_calories = sum(meal['calories'] for meal in meals)
    total_protein = sum(meal['protein'] for meal in meals)
    total_fat = sum(meal['fat'] for meal in meals)
    total_carbs = sum(meal['carbs'] for meal in meals)

    cursor.close()
    conn.close()

    return render_template('index.html', students=students, meals=meals, today=today,
                           total_calories=total_calories, total_protein=total_protein,
                           total_fat=total_fat, total_carbs=total_carbs)


@app.route('/student_portal')
def student_portal():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id = 12")
    student = cursor.fetchone()

    cursor.execute("SELECT * FROM attendance")
    attendance = cursor.fetchall()

    cursor.execute("SELECT * FROM fee_payments")
    fee_payments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student_portal.html', student=student, attendance=attendance, fee_payments=fee_payments)
from flask import jsonify, request, redirect

@app.route('/update_profile', methods=['POST'])
def update_profile():
    try:
        phone = request.form.get('phone')
        address = request.form.get('address')
        emergency_contact_name = request.form.get('emergency-contact')
        emergency_contact_number = request.form.get('emergency-number')
        if not all([phone, address, emergency_contact_name, emergency_contact_number]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "error": "Database connection failed"}), 500

        cursor = conn.cursor()
        cursor.execute('''
            UPDATE students
            SET phone = %s, address = %s, emergency_contact_name = %s, 
                emergency_contact_number = %s
            WHERE id = 1
        ''', (phone, address, emergency_contact_name, emergency_contact_number))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "redirect": "/student_portal"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500




@app.route('/food')
def food():
    current_day = datetime.now().strftime('%A')

    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT meal_type, meal_description, calories, protein, fat, carbs
        FROM weekly_menu
        WHERE day = %s
        ORDER BY FIELD(meal_type, 'Breakfast', 'Lunch', 'Dinner');
    ''', (current_day,))
    meals = cursor.fetchall()

    total_calories = sum(meal['calories'] if meal['calories'] is not None else 0 for meal in meals)
    total_protein = sum(meal['protein'] if meal['protein'] is not None else 0 for meal in meals)
    total_fat = sum(meal['fat'] if meal['fat'] is not None else 0 for meal in meals)
    total_carbs = sum(meal['carbs'] if meal['carbs'] is not None else 0 for meal in meals)

    cursor.close()
    conn.close()

    return render_template('food.html', 
                           current_day=current_day, 
                           meals=meals,
                           total_calories=total_calories,
                           total_protein=total_protein,
                           total_fat=total_fat,
                           total_carbs=total_carbs)


@app.route('/submit_dietary_request', methods=['POST'])
def submit_dietary_request():
    name = request.form['name']
    room_number = request.form['room-number']
    allergies = request.form['allergies']
    special_request = request.form['special-request']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO dietary_requests (name, room_number, allergies, special_request)
        VALUES (%s, %s, %s, %s)
    ''', (name, room_number, allergies, special_request))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "redirect": "/student_portal"}), 200


@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    student_id = request.form['student-id']
    meal_type = request.form['meal-type']
    rating = request.form['rating']
    feedback_text = request.form['feedback-comments']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO meal_feedback (student_id, meal_type, rating, feedback_text)
        VALUES (%s, %s, %s, %s)
    ''', (student_id, meal_type, rating, feedback_text))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "redirect": "/student_portal"}), 200


@app.route('/requests')
def display_requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT students.name, students.room_number, requests.request_type, requests.description, 
               requests.urgency_level, requests.status, requests.submitted_date
        FROM requests
        JOIN students ON requests.student_id = students.id
    """)
    requests_data = cursor.fetchall()

    requests = [
        {
            'student_name': row['name'],
            'room_number': row['room_number'],
            'request_type': row['request_type'],
            'description': row['description'],
            'urgency_level': row['urgency_level'],
            'status': row['status'],
            'submitted_date': row['submitted_date']
        }
        for row in requests_data
    ]

    cursor.close()
    conn.close()

    return render_template('request.html', requests=requests)

@app.route('/submit_request', methods=['POST'])
def submit_request():
    try:
        
        student_id = request.form.get('student-id')
        request_type = request.form.get('request-type')
        description = request.form.get('request-description')
        urgency = request.form.get('urgency-level')

        if not (student_id and request_type and description and urgency):
            return jsonify({'message': 'All fields are required.'}), 400

        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(''' 
            INSERT INTO requests (student_id, request_type, description, urgency_level, status, submitted_date) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (student_id, request_type, description, urgency, 'pending', datetime.now()))

    
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'Request submitted successfully!'})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': f'Error submitting request: {str(e)}'}), 500


@app.route('/complaint')
def complaints():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM complaints ORDER BY submitted_date DESC")
    complaints = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('complaints.html', complaints=complaints)

@app.route('/submit-complaint', methods=['POST'])
def submit_complaint():

    data = request.json
    student_id = data['student_id']
    title = data['title']
    description = data['description']
    category = data['category']
    submitted_date = datetime.now()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO complaints (student_id, title, description, category, status, submitted_date)
                      VALUES (%s, %s, %s, %s, %s, %s)''',
                   (student_id, title, description, category, 'pending', submitted_date))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Complaint submitted successfully!'})

@app.route('/fee')
def fee_amounts():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT amount_paid, transaction_id, payment_date AS date, status
        FROM fee_payments;
    ''')
    payments = cursor.fetchall()

    total_fee = sum(item['amount_paid'] for item in payments)
    paid_amount = sum(item['amount_paid'] for item in payments if item['status'] == 'paid')
    pending_amount = sum(item['amount_paid'] for item in payments if item['status'] == 'pending')

    cursor.close()
    conn.close()

    return render_template(
        'fee_payment.html',
        payments=payments,  
        total_fee=total_fee,
        paid_amount=paid_amount,
        pending_amount=pending_amount
    )

@app.route('/payment', methods=['POST'])
def payment():
    if request.method == 'POST':
 
        student_id = request.form['student_id']
        amount = request.form['amount']
        status = 'Pending'  
        
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed", 500

        cursor = conn.cursor(dictionary=True)


        cursor.execute('''
            INSERT INTO fee_payments (student_id, amount_paid, status)
            VALUES (%s, %s, %s)
        ''', (student_id, amount, status))

 
        conn.commit()
        cursor.close()
        conn.close()


        flash('Payment record has been added successfully!', 'success')
        return jsonify({'message': 'Complaint submitted successfully!'})
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str

@app.route('/visitor', methods=['GET', 'POST'])
def visitor_management():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)


    if request.method == 'POST' and 'visitor-name' in request.form:
        name = request.form['visitor-name']
        relation = request.form['visitor-relation']
        visit_date = request.form['visit-date']
        
        cursor.execute("""
            INSERT INTO visitors (visitor_name, relation, visit_date) 
            VALUES (%s, %s, %s)
        """, (name, relation, visit_date))
        conn.commit()


        qr_data = f"Visitor: {name}, Date: {visit_date}"
        qr_code_img = generate_qr_code(qr_data)
        
        flash('Visitor registered successfully!', 'success')
        cursor.close()
        return render_template('visitor.html', qr_code_img=qr_code_img)


    elif request.method == 'POST' and 'feedback-text' in request.form:
        rating = request.form.get('rating', 0)
        feedback_text = request.form['feedback-text']
        
        cursor.execute("""
            INSERT INTO visfeedback (rating, feedback_text) 
            VALUES (%s, %s)
        """, (rating, feedback_text))
        conn.commit()
        flash('Thank you for your feedback!', 'success')
        cursor.close()


    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, visitor_name, relation, visit_date, check_in_time, check_out_time, status 
        FROM visitors
    """)
    visitors = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('visitor.html', visitors=visitors)



if __name__ == '__main__':
    app.run(debug=True)

