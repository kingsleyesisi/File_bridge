from flask import Flask, render_template, request, url_for, redirect, session, send_file
from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room, emit
import os
import base64
import socket
from io import BytesIO

app = Flask(__name__)
app.config["SECRET_KEY"] = 'This is my Secret Key '
app.config["SESSION_TYPE"] = 'filesystem'

host = socket.gethostbyname(socket.gethostname())
# host = "wifi ip_address here"
Session(app)

# DOWNLOAD = os.path.join(app.root_path, 'uploaded_files')
# os.makedirs(DOWNLOAD, exist_ok=True)

socketio = SocketIO(app, manage_session=False)

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

@app.route('/download_temp/<file_name>')
def download_temp_file(file_name):
    file_data = request.args.get('file_data')
    file_bytes = base64.b64decode(file_data.split(",")[1])
    file_stream = BytesIO(file_bytes)
    file_stream.seek(0)
    return send_file(file_stream, as_attachment=True, attachment_filename=file_name)

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
    emit('message', {
       "msg": f"{username}: {message['msg']}"
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
   emit('message', {
       'file': data['file'],
       'fileName': data['fileName'],
       'username': session.get('username')
    }, room=Room_Name)

if __name__ == '__main__':
    socketio.run(app, debug="True", port="2024")
