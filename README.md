# SRM-HOSTEL
🏨 Student Hostel Management System
A full-stack web application for managing student life in a hostel environment, including meals, complaints, feedback, visitor management, fee tracking, and personal information updates.

🚀 Features
✅ Student portal with attendance and fee tracking

🍽️ Daily meal plan with nutritional analysis

📦 Request & complaint submission system

💳 Fee payment record and tracking

📋 Feedback system for meals and visitors

🧾 QR code generation for visitor registration

🏥 Emergency contact and profile update support

💻 Technologies Used
Backend: Flask (Python)

Frontend: HTML, CSS (via Flask templates)

Database: MySQL / MariaDB

QR Code: qrcode Python library

ORM/Connection: mysql-connector-python, Flask-MySQLdb

🛠️ Setup Instructions
🔧 Requirements
Python 3.7+

MySQL Server

pip (Python package manager)

📦 Install Dependencies
bash
Copy
Edit
pip install Flask mysql-connector-python Flask-MySQLdb qrcode
🗄️ Configure MySQL
Create a database named (e.g., hostel_db)

Run the SQL script (schema.sql) or refer to the MySQL Queries section below to create the necessary tables.

Update your credentials in the db_config in app.py:

python
Copy
Edit
db_config = {
    'host': 'YOUR_MYSQL_HOST',
    'user': 'YOUR_MYSQL_USERNAME',
    'password': 'YOUR_MYSQL_PASSWORD',
    'database': 'YOUR_DATABASE_NAME',
}
▶️ Running the App
bash
Copy
Edit
python app.py
Visit: http://localhost:5000 in your browser.

🧠 MySQL Tables
students

weekly_menu

attendance

fee_payments

dietary_requests

meal_feedback

requests

complaints

visitors

visfeedback

See this section for the full SQL schema.

📷 Screenshots (optional)
Add screenshots of your homepage, student portal, complaint form, etc.

✅ To-Do / Enhancements
Admin panel for reviewing requests and complaints

Authentication (login/signup for students & staff)

SMS/email notifications

Automatic attendance with face recognition (future AI enhancement)

📁 Folder Structure
bash
Copy
Edit
/project-root
│
├── templates/              # HTML templates
│   ├── index.html
│   ├── student_portal.html
│   ├── fee_payment.html
│   └── ...
├── static/                 # CSS/JS/images (optional)
├── app.py                  # Main Flask app
└── README.md
📄 License
This project is open-source and available under the MIT License.

database:

✅ 1. students Table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_number VARCHAR(20),
    room_number VARCHAR(10)
);
✅ 2. weekly_menu Table

CREATE TABLE weekly_menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day VARCHAR(15),
    meal_type ENUM('Breakfast', 'Lunch', 'Dinner'),
    meal_description TEXT,
    calories INT,
    protein INT,
    fat INT,
    carbs INT
);
✅ 3. attendance Table
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    date DATE,
    status ENUM('Present', 'Absent', 'Late'),
    FOREIGN KEY (student_id) REFERENCES students(id)
);
✅ 4. fee_payments Table

CREATE TABLE fee_payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    amount_paid DECIMAL(10, 2),
    transaction_id VARCHAR(100),
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('paid', 'pending'),
    FOREIGN KEY (student_id) REFERENCES students(id)
);
✅ 5. dietary_requests Table
CREATE TABLE dietary_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    room_number VARCHAR(10),
    allergies TEXT,
    special_request TEXT
);
✅ 6. meal_feedback Table
CREATE TABLE meal_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    meal_type VARCHAR(20),
    rating INT,
    feedback_text TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
✅ 7. requests Table

CREATE TABLE requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    request_type VARCHAR(100),
    description TEXT,
    urgency_level ENUM('low', 'medium', 'high'),
    status ENUM('pending', 'resolved', 'in_progress') DEFAULT 'pending',
    submitted_date DATETIME,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
✅ 8. complaints Table
CREATE TABLE complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    title VARCHAR(255),
    description TEXT,
    category VARCHAR(100),
    status ENUM('pending', 'reviewed', 'resolved') DEFAULT 'pending',
    submitted_date DATETIME,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
✅ 9. visitors Table
CREATE TABLE visitors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    visitor_name VARCHAR(100),
    relation VARCHAR(50),
    visit_date DATE,
    check_in_time TIME DEFAULT NULL,
    check_out_time TIME DEFAULT NULL,
    status ENUM('pending', 'checked_in', 'checked_out') DEFAULT 'pending'
);
✅ 10. visfeedback Table
CREATE TABLE visfeedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rating INT,
    feedback_text TEXT
);
🚀 Sample Insertions (for testing)

-- Sample student
INSERT INTO students (name, phone, address, emergency_contact_name, emergency_contact_number, room_number)
VALUES ('John Doe', '1234567890', 'Dorm 5, Block B', 'Jane Doe', '0987654321', 'A101');

-- Sample weekly menu
INSERT INTO weekly_menu (day, meal_type, meal_description, calories, protein, fat, carbs)
VALUES ('Monday', 'Breakfast', 'Omelette and Toast', 300, 15, 10, 30);

-- Sample fee payment
INSERT INTO fee_payments (student_id, amount_paid, status)
VALUES (1, 5000.00, 'paid');
