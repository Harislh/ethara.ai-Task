# Team Task Manager

A simple web-based Task Management System built using Flask and MySQL.  
Supports Admin and User roles with project, task, and member management.

---

## Features

- User Signup & Login (Admin / Member)
- Admin Dashboard
  - Add / Update / Delete Members
  - Create / Delete Projects
  - Assign Tasks to Members
  - View Tasks and Team Status (Free / Busy)
- User Dashboard
  - View Assigned Tasks
  - Update Task Status
  - Change Password
- Flash Messages (Success / Error)
- Responsive UI (White / Black / Ash theme)

---

## Tech Stack

- Python (Flask)
- MySQL
- HTML / CSS
- Jinja2

---

## Project Structure

task-manager/
│
├── app.py
├── config.py
├── requirements.txt
├── readme.txt
├── templates/
│ ├── index.html
│ ├── admindashboard.html
│ ├── userdashboard.html