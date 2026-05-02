from flask import Flask, render_template, request, redirect, session, flash
import config

app = Flask(__name__)
app.secret_key = config.get_secret_key()

def get_db():
    return config.get_db_connection()


# LOGIN PAGE
@app.route('/')
def login_page():
    return render_template('index.html')


# SIGNUP
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        flash("Email already exists", "error")
        return redirect('/')

    cur.execute("INSERT INTO users(name,email,password,role) VALUES(%s,%s,%s,%s)",
                (name, email, password, role))

    db.commit()
    db.close()

    flash("Signup successful", "success")
    return redirect('/')


# LOGIN
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT id, role FROM users WHERE email=%s AND password=%s",
                (email, password))

    user = cur.fetchone()
    db.close()

    if user:
        if user[1] != role:
            flash("Wrong role selected", "error")
            return redirect('/')

        session['user_id'] = user[0]
        session['role'] = user[1]

        return redirect('/admin' if role == 'admin' else '/user')

    flash("Invalid credentials", "error")
    return redirect('/')


# ADMIN DASHBOARD
@app.route('/admin')
def admin():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/')

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT u.id, u.emp_id, u.name, u.email,
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM tasks t 
                WHERE t.assigned_to = u.id AND t.status != 'done'
            ) THEN 'Busy'
            ELSE 'Free'
        END
        FROM users u WHERE u.role='member'
    """)
    members = cur.fetchall()

    cur.execute("""
        SELECT p.id, p.name, p.description, p.deadline,
        GROUP_CONCAT(u.name SEPARATOR ', ')
        FROM projects p
        LEFT JOIN tasks t ON p.id=t.project_id
        LEFT JOIN users u ON t.assigned_to=u.id
        GROUP BY p.id
    """)
    projects = cur.fetchall()

    cur.execute("""
        SELECT t.id, t.title, t.status, u.name, p.name, p.deadline
        FROM tasks t
        JOIN users u ON t.assigned_to=u.id
        JOIN projects p ON t.project_id=p.id
    """)
    tasks = cur.fetchall()

    db.close()

    return render_template('admindashboard.html',
                           members=members,
                           projects=projects,
                           tasks=tasks)


# ADD MEMBER
@app.route('/add_member', methods=['POST'])
def add_member():
    db = get_db()
    cur = db.cursor()
    idP = request.form['emp_id']
    cur.execute("""
        INSERT INTO users(emp_id,name,email,password,role)
        VALUES(%s,%s,%s,%s,'member')
    """, (idP, request.form['name'], request.form['email'],idP))

    db.commit()
    db.close()

    flash("Member added", "success")
    return redirect('/admin')


# UPDATE MEMBER
@app.route('/update_member/<int:id>', methods=['POST'])
def update_member(id):
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        UPDATE users SET name=%s,email=%s WHERE id=%s
    """, (request.form['name'], request.form['email'], id))

    db.commit()
    db.close()

    return redirect('/admin')


# DELETE MEMBER
@app.route('/delete_member/<int:id>')
def delete_member(id):
    db = get_db()
    cur = db.cursor()

    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    db.commit()
    db.close()

    return redirect('/admin')


# CREATE PROJECT
@app.route('/create_project', methods=['POST'])
def create_project():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        INSERT INTO projects(name,description,deadline,created_by)
        VALUES(%s,%s,%s,%s)
    """, (
        request.form['name'],
        request.form['description'],
        request.form['deadline'],
        session['user_id']
    ))

    db.commit()
    db.close()

    return redirect('/admin')


# DELETE PROJECT
@app.route('/delete_project/<int:id>')
def delete_project(id):
    db = get_db()
    cur = db.cursor()

    cur.execute("DELETE FROM projects WHERE id=%s", (id,))
    db.commit()
    db.close()

    return redirect('/admin')


# ASSIGN TASK
@app.route('/assign_task', methods=['POST'])
def assign_task():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        INSERT INTO tasks(title,description,assigned_to,project_id)
        VALUES(%s,%s,%s,%s)
    """, (
        request.form['title'],
        request.form['description'],
        request.form['assigned_to'],
        request.form['project_id']
    ))

    db.commit()
    db.close()

    flash("Task assigned", "success")
    return redirect('/admin')


# USER DASHBOARD
@app.route('/user')
def user():
    if 'user_id' not in session:
        return redirect('/')

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT t.id, t.title, t.status, p.name, p.deadline
        FROM tasks t
        JOIN projects p ON t.project_id=p.id
        WHERE t.assigned_to=%s
    """, (session['user_id'],))

    tasks = cur.fetchall()
    db.close()

    return render_template('userdashboard.html', tasks=tasks)


# UPDATE TASK
@app.route('/update_my_task/<int:id>', methods=['POST'])
def update_my_task(id):
    db = get_db()
    cur = db.cursor()

    cur.execute("UPDATE tasks SET status=%s WHERE id=%s",
                (request.form['status'], id))

    db.commit()
    db.close()

    flash("Task updated", "success")
    return redirect('/user')


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)