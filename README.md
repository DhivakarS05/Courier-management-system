# Courier Management System (Python Flask)

## 📌 Project Overview

The **Courier Management System** is a web-based application developed using **Python Flask** and **MySQL**.
It allows customers to book couriers, admins to manage staff and assignments, and staff to update delivery status.

This project demonstrates full-stack development skills including authentication, role-based access, database integration, and CRUD operations.

---

## 🚀 Features

### 👤 Customer

* User registration & login
* Book courier with cost calculation
* Generate unique tracking ID
* View courier history
* Track courier status
* Cancel courier (before assignment)

### 🧑‍💼 Admin

* Admin login
* Manage staff (Add / Edit / Delete)
* View customers
* Assign couriers to staff
* View all couriers & tracking IDs

### 🧑‍🔧 Staff

* Staff login
* View assigned couriers
* Update courier delivery status

---

## 🛠️ Technologies Used

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, Jinja Templates
* **Database:** MySQL
* **Tools:** Git, GitHub

---

## 📂 Project Structure

```
project-folder/
│── app.py
│── templates/
│── static/
│── README.md
```

---

## ⚙️ How to Run This Project (Step-by-Step)

### 1️⃣ Install Python

Download and install Python (3.8+):
[https://www.python.org/downloads/](https://www.python.org/downloads/)

Verify installation:

```bash
python --version
```

---

### 2️⃣ Install Required Libraries

Open terminal / command prompt inside the project folder:

```bash
pip install flask mysql-connector-python reportlab
```

---

### 3️⃣ Setup MySQL Database

Create a database named:

```sql
CREATE DATABASE courier_db;
```

Create required tables:

* users
* admins
* staff
* couriers

(Use MySQL Workbench or phpMyAdmin)

⚠️ Update database credentials in **app.py**:

```python
host="localhost"
user="courier_user"
password="CourierPass123!"
database="courier_db"
```

---

### 4️⃣ Run the Application

```bash
python app.py
```

---

### 5️⃣ Open in Browser

```
http://127.0.0.1:5000/
```

---

## 🔐 Login Pages

* Customer Login: `/login_user`
* Admin Login: `/login_admin`
* Staff Login: `/login_staff`

---

## 🎯 Purpose of the Project

This project was developed to:

* Understand Python Flask framework
* Implement real-world role-based systems
* Work with MySQL databases
* Practice full-stack development

---

## 👨‍🎓 Developed By

**Dhivakar S**
MCA Graduate | Python Full-Stack Developer (Fresher)
GitHub: https://github.com/DhivakarS05
