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
socketio = SocketIO(app, manage_session=False)

# Define Models
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
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

@app.route('/receiver', methods=["GET", "POST"])
def receiver():
    return render_template('share/receiver.html')

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
        "download_count": file_record.download_count
    })

@app.route('/room_files/<room_name>')
def room_files(room_name):
    if session.get('Room_Name') != room_name:
        return jsonify({"error": "Access denied"}), 403
    
    files = File.query.filter_by(room_name=room_name).order_by(File.timestamp.desc()).all()
    file_stream = BytesIO(file_record.data)
    file_stream.seek(0)
    
    file_list = []
    for file_record in files:
        file_list.append({
            "id": file_record.id,
            "filename": file_record.filename,
            "file_size": file_record.file_size,
            "username": file_record.username,
            "timestamp": file_record.timestamp.isoformat(),
            "download_count": file_record.download_count
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
    join_room(Room_Name)
    emit('status', {
        "msg": f"{username} has joined the room!!!"
    }, room=Room_Name)

@socketio.on('text', namespace='/sender')
def text_event(message):
    Room_Name = session.get('Room_Name')
    username = session.get('username')
    content = message['msg']

    # Save message to the database
    new_message = Message(room_name=Room_Name, username=username, content=content)
    db.session.add(new_message)
    db.session.commit()

    emit('message', {
        "msg": f"{username}: {content}"
    }, room=Room_Name)

@socketio.on('left', namespace='/sender')
def left_event(message):
    Room_Name = session.get('Room_Name')
    username = session.get('username')
    leave_room(Room_Name)
    session.clear()
    emit('status', {
        "msg": f"{username} has left the room :("
    }, room=Room_Name)

@socketio.on('file', namespace='/sender')
def handle_file(data):
    Room_Name = session.get('Room_Name')
    username = session.get('username')
    filename = data['fileName']
    file_size = data.get('fileSize', 0)
    file_type = data.get('fileType', '')
    file_data = base64.b64decode(data['file'].split(",")[1])
    
    # Validate file size (50MB limit)
    max_size = 50 * 1024 * 1024  # 50MB
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

    emit('message', {
        'file': filename,
        'file_id': new_file.id,
        'username': username,
        'fileSize': file_size,
        'fileType': file_type
    }, room=Room_Name)

@socketio.on('error_handler', namespace='/sender')
def handle_error(error):
    print(f"SocketIO Error: {error}")
    emit('error', {'msg': 'An error occurred. Please try again.'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, port=2024)
