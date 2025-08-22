from flask import Flask, render_template, request, url_for, redirect, session, send_file, jsonify
from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import base64
from io import BytesIO
import datetime
import uuid
import hashlib
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://default:gN9Zeldkmb6P@ep-patient-bar-a49hhlnc-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Session configuration
app.config["SESSION_TYPE"] = 'sqlalchemy'
app.config["SESSION_SQLALCHEMY"] = db  # Use the existing db instance
app.config["SESSION_PERMANENT"] = False

# Initialize Flask-Session
Session(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-SocketIO
socketio = SocketIO(app, manage_session=False, async_mode='eventlet', cors_allowed_origins='*')

# Store active users and typing status
active_users = {}
typing_users = {}

# Define Models
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # 'text', 'code', 'file'
    user_color = db.Column(db.String(7), nullable=True)  # Hex color for user
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False, default=0)
    file_type = db.Column(db.String(100), nullable=True)
    data = db.Column(db.LargeBinary, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)
    file_uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))

def generate_user_color(username):
    """Generate a consistent color for a user based on their username"""
    hash_object = hashlib.md5(username.encode())
    hex_dig = hash_object.hexdigest()
    # Use first 6 characters as color, but ensure it's not too light
    color = '#' + hex_dig[:6]
    # Ensure the color is dark enough for readability
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    if (r + g + b) > 400:  # Too light
        r, g, b = max(0, r - 100), max(0, g - 100), max(0, b - 100)
        color = f'#{r:02x}{g:02x}{b:02x}'
    return color

def detect_code_block(content):
    """Detect if content contains code blocks"""
    code_patterns = [
        r'```[\s\S]*?```',  # Triple backticks
        r'`[^`\n]+`',       # Single backticks
        r'^\s*(def |class |import |from |if __name__|for |while |try:|except:|with |async |await)',  # Python
        r'^\s*(function |var |let |const |if |for |while |try |catch|async |await|export |require)',  # JavaScript
        r'^\s*(public |private |class |interface |import |package|extends |implements)',  # Java
        r'^\s*(#include|int main|void |char |float |double|struct |typedef)',  # C/C++
        r'^\s*(SELECT |INSERT |UPDATE |DELETE |CREATE |ALTER |DROP)',  # SQL
        r'^\s*(<!DOCTYPE|<html|<head|<body|<div|<span|<p>)',  # HTML
        r'^\s*(\.|#)[a-zA-Z-_].*\{',  # CSS
        r'^\s*(using |namespace |public class|private |protected)',  # C#
        r'^\s*(func |var |let |if |for |while |switch)',  # Swift/Go
        r'^\s*(fn |let |mut |impl |struct |enum|match)',  # Rust
        r'.*[{}();].*',  # General programming syntax
        r'.*(\+\+|--|==|!=|<=|>=|\|\||&&)',  # Programming operators
    ]
    
    for pattern in code_patterns:
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            return True
    
    # Check for multiple lines with indentation (likely code)
    lines = content.split('\n')
    if len(lines) > 2:
        indented_lines = sum(1 for line in lines if line.startswith('    ') or line.startswith('\t'))
        if indented_lines >= len(lines) * 0.3:  # 30% of lines are indented
            return True
    
    return False

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/sender', methods=["GET", "POST"])
def sender():
    if request.method == "POST":
        username = request.form["username"]
        room_name = request.form["Room_Name"]
        session["username"] = username
        session["Room_Name"] = room_name
        return render_template('share/sender.html', Session=session)
    elif session.get('username') is not None:
        return render_template('share/receiver.html', Session=session)
    else:
        return redirect(url_for('receiver'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/download_temp/<file_id>')
def download_temp_file(file_id):
    try:
        file_record = File.query.get(file_id)
        if not file_record:
            return "File not found", 404
        
        # Increment download count
        file_record.download_count += 1
        db.session.commit()
        
        file_stream = BytesIO(file_record.data)
        file_stream.seek(0)
        
        return send_file(
            file_stream, 
            as_attachment=True, 
            download_name=file_record.filename,
            mimetype=file_record.file_type or 'application/octet-stream'
        )
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route('/file_link/<file_uuid>')
def file_link(file_uuid):
    """Shareable file link"""
    try:
        file_record = File.query.filter_by(file_uuid=file_uuid).first()
        if not file_record:
            return "File not found", 404
        
        # Increment download count
        file_record.download_count += 1
        db.session.commit()
        
        file_stream = BytesIO(file_record.data)
        file_stream.seek(0)
        
        return send_file(
            file_stream, 
            as_attachment=True, 
            download_name=file_record.filename,
            mimetype=file_record.file_type or 'application/octet-stream'
        )
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route('/file_info/<file_id>')
def file_info(file_id):
    file_record = File.query.get(file_id)
    if not file_record:
        return jsonify({"error": "File not found"}), 404
    
    return jsonify({
        "filename": file_record.filename,
        "file_size": file_record.file_size,
        "file_type": file_record.file_type,
        "upload_time": file_record.timestamp.isoformat(),
        "download_count": file_record.download_count,
        "shareable_link": url_for('file_link', file_uuid=file_record.file_uuid, _external=True)
    })

@app.route('/room_files/<room_name>')
def room_files(room_name):
    if session.get('Room_Name') != room_name:
        return jsonify({"error": "Access denied"}), 403
    
    files = File.query.filter_by(room_name=room_name).order_by(File.timestamp.desc()).all()
    
    file_list = []
    for file_record in files:
        file_list.append({
            "id": file_record.id,
            "filename": file_record.filename,
            "file_size": file_record.file_size,
            "username": file_record.username,
            "timestamp": file_record.timestamp.isoformat(),
            "download_count": file_record.download_count,
            "shareable_link": url_for('file_link', file_uuid=file_record.file_uuid, _external=True)
        })
    
    return jsonify({"files": file_list})

@app.route('/instructions')
def instructions():
    return render_template('instructions/instructions.html')

@app.route('/Downloads')
def to_downloads():
    return render_template('Downloads/Downloads.html')

@socketio.on('sender', namespace='/sender')
def sender_event(message):
    Room_Name = session.get('Room_Name')
    username = session.get('username')
    user_color = generate_user_color(username)
    
    join_room(Room_Name)
    
    # Add user to active users
    if Room_Name not in active_users:
        active_users[Room_Name] = {}
    active_users[Room_Name][username] = {
        'color': user_color,
        'session_id': request.sid
    }
    
    # Emit updated user list
    emit('user_list_update', {
        'users': list(active_users[Room_Name].keys()),
        'user_count': len(active_users[Room_Name])
    }, room=Room_Name)
    
    emit('status', {
        "msg": f"{username} has joined the room!!!",
        "type": "join"
    }, room=Room_Name)

@socketio.on('text', namespace='/sender')
def text_event(message):
    Room_Name = session.get('Room_Name')
    username = session.get('username')
    content = message['msg']
    user_color = generate_user_color(username)
    
    # Detect if content is code
    message_type = 'code' if detect_code_block(content) else 'text'

    # Save message to the database
    new_message = Message(
        room_name=Room_Name, 
        username=username, 
        content=content,
        message_type=message_type,
        user_color=user_color
    )
    db.session.add(new_message)
    db.session.commit()

    emit('message', {
        "username": username,
        "content": content,
        "message_type": message_type,
        "user_color": user_color,
        "timestamp": new_message.timestamp.isoformat()
    }, room=Room_Name)

@socketio.on('typing', namespace='/sender')
def typing_event(data):
    Room_Name = session.get('Room_Name')
    username = session.get('username')
    action = data.get('action', 'typing')
    
    if Room_Name not in typing_users:
        typing_users[Room_Name] = {}
    
    if data['typing']:
        typing_users[Room_Name][username] = {
            'action': action,
            'username': username
        }
    else:
        typing_users[Room_Name].pop(username, None)
    
    # Remove current user from typing list when emitting
    typing_list = [user_data for user, user_data in typing_users.get(Room_Name, {}).items() if user != username]
    
    emit('typing_update', {
        'typing_users': typing_list
    }, room=Room_Name, include_self=False)

@socketio.on('left', namespace='/sender')
def left_event(message):
    Room_Name = session.get('Room_Name')
    username = session.get('username')
    
    leave_room(Room_Name)
    
    # Remove user from active users
    if Room_Name in active_users and username in active_users[Room_Name]:
        del active_users[Room_Name][username]
        if not active_users[Room_Name]:  # Remove room if empty
            del active_users[Room_Name]
    
    # Remove from typing users
    if Room_Name in typing_users:
        typing_users[Room_Name].pop(username, None)
    
    # Emit updated user list
    if Room_Name in active_users:
        emit('user_list_update', {
            'users': list(active_users[Room_Name].keys()),
            'user_count': len(active_users[Room_Name])
        }, room=Room_Name)
    
    emit('status', {
        "msg": f"{username} has left the room :(",
        "type": "leave"
    }, room=Room_Name)
    
    # Clear session after emitting
    session.clear()

@socketio.on('file', namespace='/sender')
def handle_file(data):
    Room_Name = session.get('Room_Name')
    username = session.get('username')
    filename = data['fileName']
    file_size = data.get('fileSize', 0)
    file_type = data.get('fileType', '')
    file_data = base64.b64decode(data['file'].split(",")[1])
    user_color = generate_user_color(username)
    
    # Validate file size (50MB limit)
    max_size = 2000 * 1024 * 1024  # 50MB
    if len(file_data) > max_size:
        emit('error', {'msg': 'File size exceeds 50MB limit'})
        return

    # Save file to the database
    new_file = File(
        room_name=Room_Name, 
        username=username, 
        filename=filename, 
        file_size=file_size,
        file_type=file_type,
        data=file_data
    )
    db.session.add(new_file)
    db.session.commit()
    
    # Save file message to database
    file_message = Message(
        room_name=Room_Name,
        username=username,
        content=f"Shared file: {filename}",
        message_type='file',
        user_color=user_color
    )
    db.session.add(file_message)
    db.session.commit()
    
    shareable_link = url_for('file_link', file_uuid=new_file.file_uuid, _external=True)

    emit('message', {
        'username': username,
        'filename': filename,
        'file_id': new_file.id,
        'file_size': file_size,
        'file_type': file_type,
        'message_type': 'file',
        'user_color': user_color,
        'shareable_link': shareable_link,
        'timestamp': new_file.timestamp.isoformat()
    }, room=Room_Name)

@socketio.on('disconnect', namespace='/sender')
def disconnect_event():
    Room_Name = session.get('Room_Name')
    username = session.get('username')
    
    if Room_Name and username:
        # Remove user from active users
        if Room_Name in active_users and username in active_users[Room_Name]:
            del active_users[Room_Name][username]
            if not active_users[Room_Name]:
                del active_users[Room_Name]
        
        # Remove from typing users
        if Room_Name in typing_users:
            typing_users[Room_Name].discard(username)
        
        # Emit updated user list
        if Room_Name in active_users:
            emit('user_list_update', {
                'users': list(active_users[Room_Name].keys()),
                'user_count': len(active_users[Room_Name])
            }, room=Room_Name)

@socketio.on('error_handler', namespace='/sender')
def handle_error(error):
    print(f"SocketIO Error: {error}")
    emit('error', {'msg': 'An error occurred. Please try again.'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    socketio.run(app, debug=True, port=8000, host='0.0.0.0', allow_unsafe_werkzeug=True)
