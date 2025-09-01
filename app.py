from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # change this for security

# Initialize databases
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    for u in [('user1','pass1'),('user2','pass2'),('user3','pass3'),('user4','pass4'),('user5','pass5')]:
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?,?)', u)
        except:
            pass
    conn.commit()
    conn.close()

    conn = sqlite3.connect('records.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Login
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    conn = sqlite3.connect('records.db')
    c = conn.cursor()
    c.execute('SELECT * FROM records')
    records = c.fetchall()
    conn.close()
    return render_template('dashboard.html', records=records, username=session['username'])

# Add record
@app.route('/add', methods=['GET','POST'])
def add():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        conn = sqlite3.connect('records.db')
        c = conn.cursor()
        c.execute('INSERT INTO records (title, description) VALUES (?,?)', (title, description))
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    return render_template('add.html')

# Edit record
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    if 'username' not in session:
        return redirect('/')
    conn = sqlite3.connect('records.db')
    c = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        c.execute('UPDATE records SET title=?, description=? WHERE id=?', (title, description, id))
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    c.execute('SELECT * FROM records WHERE id=?', (id,))
    record = c.fetchone()
    conn.close()
    return render_template('edit.html', record=record)

# Delete record
@app.route('/delete/<int:id>')
def delete(id):
    if 'username' not in session:
        return redirect('/')
    conn = sqlite3.connect('records.db')
    c = conn.cursor()
    c.execute('DELETE FROM records WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
