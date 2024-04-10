from flask import Flask, render_template, redirect, url_for, session, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'b89a7524427924a1ef513c14cf96ecbd'

# Ensure the UPLOAD_FOLDER exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set the UPLOAD_FOLDER where uploaded files will be saved
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Mock user credentials (you should implement a proper authentication system)
USERNAME = 'admin'
PASSWORD = 'password'

# Sample posts with initial likes count (replace this with actual database integration)
posts = [
    {'title': 'First Post', 'content': 'This is my first post.', 'likes': 0},
    {'title': 'Second Post', 'content': 'This is my second post.', 'likes': 0}
]

# Function to check if user is logged in
def is_logged_in():
    return 'logged_in' in session

# Function to check if user is authorized to create posts
def is_authorized():
    return session.get('username') == USERNAME

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html', is_logged_in=is_logged_in(), is_authorized=is_authorized(), posts=posts)

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if is_logged_in() and is_authorized():
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            image_url = None
            video_url = None
            
            # Handle image upload if provided
            if 'image' in request.files and request.files['image'].filename:
                image = request.files['image']
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)
                image_url = url_for('uploaded_file', filename=image_filename)
                
            # Handle video upload if provided
            if 'video' in request.files and request.files['video'].filename:
                video = request.files['video']
                video_filename = secure_filename(video.filename)
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
                video.save(video_path)
                video_url = url_for('uploaded_file', filename=video_filename)
                
            new_post = {'title': title, 'content': content, 'image_url': image_url, 'video_url': video_url, 'likes': 0}
            posts.append(new_post)
            return redirect(url_for('index'))
        return render_template('create_post.html')
    else:
        return redirect(url_for('index'))

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if is_logged_in() and is_authorized():
        if post_id < len(posts):
            del posts[post_id]
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if post_id < len(posts):
        posts[post_id]['likes'] += 1
    return jsonify({'success': True})

# Route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
