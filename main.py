
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

# Flask app initialization
app = Flask(__name__)
app.secret_key = 'kusumachandashwini'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12032002@localhost/students'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Models
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

class Department(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(100))

class Attendance(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(100))
    attendance = db.Column(db.Integer())

class Trig(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(100))
    action = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(1000))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(50))
    sname = db.Column(db.String(50))
    sem = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    branch = db.Column(db.String(50))
    email = db.Column(db.String(50))
    number = db.Column(db.String(12))
    address = db.Column(db.String(100))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/studentdetails')
def studentdetails():
    stmt = text("SELECT * FROM student")
    with db.engine.connect() as connection:
        query = connection.execute(stmt)
    return render_template('studentdetails.html', query=query)

@app.route('/triggers')
def triggers():
    stmt = text("SELECT * FROM trig")
    with db.engine.connect() as connection:
        query = connection.execute(stmt)
    return render_template('triggers.html', query=query)

@app.route('/department', methods=['POST', 'GET'])
def department():
    if request.method == "POST":
        dept = request.form.get('dept')
        query = Department.query.filter_by(branch=dept).first()
        if query:
            flash("Department Already Exist", "warning")
            return redirect('/department')
        dep = Department(branch=dept)
        db.session.add(dep)
        db.session.commit()
        flash("Department Added", "success")
    return render_template('department.html')

@app.route('/addattendance', methods=['POST', 'GET'])
def addattendance():
    stmt = text("SELECT * FROM student")
    with db.engine.connect() as connection:
        query = connection.execute(stmt)
    
    if request.method == "POST":
        rollno = request.form.get('rollno')
        attend = request.form.get('attend')
        atte = Attendance(rollno=rollno, attendance=attend)
        db.session.add(atte)
        db.session.commit()
        flash("Attendance added", "warning")
    
    return render_template('attendance.html', query=query)

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        rollno = request.form.get('roll')
        bio = Student.query.filter_by(rollno=rollno).first()
        attend = Attendance.query.filter_by(rollno=rollno).first()

        if not bio:
            flash(f"Student with roll number {rollno} not found", "warning")
        if not attend:
            flash(f"Attendance for {rollno} not found", "warning")
        
        return render_template('search.html', bio=bio, attend=attend)

    return render_template('search.html')

@app.route("/delete/<string:id>", methods=['POST', 'GET'])
@login_required
def delete(id):
    try:
        db.session.execute(text(f"DELETE FROM student WHERE student.id={id}"))
        db.session.commit()
        flash("Slot Deleted Successfully", "danger")
    except Exception as e:
        db.session.rollback()
        flash("Error occurred while deleting the student", "danger")
    return redirect('/studentdetails')

@app.route("/edit/<string:id>", methods=['POST', 'GET'])
@login_required
def edit(id):
    stmt = text("SELECT * FROM department")
    with db.engine.connect() as connection:
        dept = connection.execute(stmt)
    
    posts = Student.query.filter_by(id=id).first()
    if request.method == "POST":
        rollno = request.form.get('rollno')
        sname = request.form.get('sname')
        sem = request.form.get('sem')
        gender = request.form.get('gender')
        branch = request.form.get('branch')
        email = request.form.get('email')
        num = request.form.get('num')
        address = request.form.get('address')
        try:
            db.session.execute(text(f"UPDATE student SET rollno='{rollno}', sname='{sname}', sem='{sem}', gender='{gender}', branch='{branch}', email='{email}', number='{num}', address='{address}' WHERE id={id}"))
            db.session.commit()
            flash("Slot Updated", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error occurred while updating the student", "danger")
        return redirect('/studentdetails')
    
    return render_template('edit.html', posts=posts, dept=dept)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist", "warning")
            return render_template('/signup.html')
        encpassword = generate_password_hash(password)

        new_user = User(username=username, email=email, password=encpassword)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup Success. Please Login", "success")
        return render_template('login.html')
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Success", "primary")
            return redirect(url_for('index'))
        else:
            flash("Invalid Credentials", "danger")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

@app.route('/addstudent', methods=['POST', 'GET'])
@login_required
def addstudent():
    stmt = text("SELECT * FROM department")
    with db.engine.connect() as connection:
        dept = connection.execute(stmt)
    
    if request.method == "POST":
        rollno = request.form.get('rollno')
        sname = request.form.get('sname')
        sem = request.form.get('sem')
        gender = request.form.get('gender')
        branch = request.form.get('branch')
        email = request.form.get('email')
        num = request.form.get('num')
        address = request.form.get('address')
        try:
            new_student = Student(rollno=rollno, sname=sname, sem=sem, gender=gender, branch=branch, email=email, number=num, address=address)
            db.session.add(new_student)
            db.session.commit()
            flash("Student Added", "info")
        except Exception as e:
            db.session.rollback()
            flash("Error occurred while adding the student", "danger")
    return render_template('student.html', dept=dept)

@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'

# Ensure tables are created
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)