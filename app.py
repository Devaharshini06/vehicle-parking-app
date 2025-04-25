from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# -------------------------
# USER MODEL
# -------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------------
# BOOKING MODEL
# -------------------------
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    spot_id = db.Column(db.Integer, nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)

# -------------------------
# ROUTES (Coming soon)
# -------------------------
@app.route('/')
def home():
    return render_template('login.html')  # Change later if needed

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_pw = generate_password_hash(password)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "warning")
            return redirect(url_for('register'))

        user = User(username=username, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        flash("Registered successfully! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            session['user_id'] = user.id  # Add this line 👈
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))  # or 'dashboard' if that's the route
 # We’ll define this later
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')
    


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out!", "info")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    bookings = Booking.query.filter_by(user_id=user.id).all()

    return render_template('dashboard.html', user=user, bookings=bookings)

def get_db_connection():
    import sqlite3
    conn = sqlite3.connect('parking_app.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book_spot():
    if request.method == 'POST':
        lot_id = request.form['lot_id']
        conn = get_db_connection()

        spot = conn.execute("SELECT * FROM spots WHERE lot_id = ? AND status = 'A' LIMIT 1", (lot_id,)).fetchone()

        if spot:
            conn.execute("UPDATE spots SET status = 'O' WHERE id = ?", (spot['id'],))
            conn.execute("""
                INSERT INTO bookings (user_id, spot_id, parking_timestamp)
                VALUES (?, ?, datetime('now'))
            """, (current_user.id, spot['id']))
            conn.commit()
            flash('Spot successfully booked!', 'success')
        else:
            flash('No available spots in this lot.', 'danger')

        conn.close()
        return redirect(url_for('dashboard'))

    return render_template('book.html')  # GET request → show form





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)




