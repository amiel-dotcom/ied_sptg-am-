import os
import firebase_admin
from firebase_admin import credentials, firestore, storage
from flask import Flask, request, jsonify, render_template, redirect, flash, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError,DataRequired, Email


cred = credentials.Certificate("sigmatauphigamma-firebase-adminsdk-fbsvc-479adfe883.json") 
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your-app-id.appspot.com'  # Replace with your Firebase Storage bucket
})

# Firebase Firestore and Storage setup
db = firestore.client()
bucket = storage.bucket()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sigmatauphigamma'
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Helper for file upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# User model for Flask-Login
class FirestoreUser(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        data = user_doc.to_dict()
        return FirestoreUser(id=user_doc.id, username=data['username'])
    return None

# Register form and Login form
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder": "Email"})
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        users = db.collection('users').where('username', '==', username.data).get()
        if users:
            raise ValidationError("Username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[DataRequired(), InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

# Create post route
@app.route('/create-post', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content')
    image = request.files.get('image')

    filename = None
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save image locally first
        image.save(image_path)

        # Upload image to Firebase Storage
        blob = bucket.blob(f"posts/{filename}")
        blob.upload_from_filename(image_path)

        # Get the URL of the uploaded image
        image_url = blob.public_url

        # Clean up the local file after uploading
        os.remove(image_path)

    # Store post data in Firestore
    post_ref = db.collection('posts').add({
        'content': content,
        'image': image_url if filename else None,
        'user_id': current_user.id,  # Save the user who posted
        'username': current_user.username  # Save the username for display
    })

    return jsonify({'message': 'Post created successfully!'}), 201

# Get posts route
@app.route('/posts', methods=['GET'])
def get_posts():
    posts_ref = db.collection('posts')
    posts = posts_ref.stream()

    result = []
    for post in posts:
        post_data = post.to_dict()
        result.append({
            'id': post.id,
            'content': post_data.get('content'),
            'image': post_data.get('image'),
            'username': post_data.get('username')  # Include username with the post
        })

    return jsonify(result)

# Dashboard route (only for logged-in users)
@app.route('/dashboard')
@login_required
def dashboard():
    print("Authenticated?", current_user.is_authenticated)
    return render_template("dashboard.html", name=current_user.username)

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_ref = db.collection('users').add({'username': form.username.data, 'password': hashed_pw})
        flash("Account created. Please log in.")
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        print("Form submitted")
        if form.validate_on_submit():
            print("Form validated")
            user_docs = db.collection('users').where('username', '==', form.username.data).get()

            if user_docs:
                print("User found")
                user_doc = user_docs[0]
                data = user_doc.to_dict()

                if bcrypt.check_password_hash(data['password'], form.password.data):
                    print("Password correct")
                    user = FirestoreUser(id=user_doc.id, username=data['username'])
                    login_user(user)
                    return redirect(url_for('dashboard'))
                else:
                    print("Invalid password")
                    flash("Invalid username or password.")
            else:
                print("Username not found")
                flash("Invalid username or password.")
        else:
            print("Form failed validation:", form.errors)

    return render_template("login.html", form=form)


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Home route
@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)
