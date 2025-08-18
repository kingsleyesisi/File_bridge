# FileBridge 🚀

Hey there! 👋 Welcome to FileBridge, your go-to solution for seamless file sharing and real-time collaboration. This project aims to make sharing files as easy as sending a message. Think of it as your personal cloud, but with a chatroom twist! 💬

[![Built with DocMint](https://img.shields.io/badge/Generated%20by-DocMint-red)](https://github.com/kingsleyesisi/DocMint)

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Troubleshooting](#troubleshooting)

## Project Overview
FileBridge is designed to simplify file sharing by creating temporary, collaborative rooms where users can exchange files and chat in real-time. No more clunky email attachments or complicated transfer services! Just create a room, invite your friends, and start sharing. 📁

## Features
- **Real-Time Chat:** Chat with room members while sharing files. See who's online and who's typing. ✍️
- **File Sharing:** Share files up to 50MB. Documents, images, videos – you name it! 🖼️
- **Temporary Rooms:** Rooms are created on the fly and exist as long as they're active. 🚪
- **Shareable Links:** Generate and share direct download links for files. 🔗
- **Code Sharing:** Share code snippets with syntax highlighting. 💻
- **User Color:** Each user gets a unique color for easier identification. 🎨
- **Mobile Responsive:** Works smoothly on all devices. 📱
- **Easy to Use:** Simple, intuitive interface for hassle-free file sharing. 🖱️

## Technologies Used
Here's a breakdown of the tech stack that powers FileBridge:

- ![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python&logoColor=white)
- ![Flask](https://img.shields.io/badge/Flask-2.x-green?style=flat-square&logo=flask&logoColor=white)
- ![Flask-SocketIO](https://img.shields.io/badge/Flask--SocketIO-5.x-orange?style=flat-square&logo=socket.io&logoColor=white)
- ![Flask-SQLAlchemy](https://img.shields.io/badge/Flask--SQLAlchemy-3.x-red?style=flat-square&logo=sqlalchemy&logoColor=white)
- ![Flask-Migrate](https://img.shields.io/badge/Flask--Migrate-4.x-yellow?style=flat-square&logo=alembic&logoColor=black)
- ![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow?style=flat-square&logo=javascript&logoColor=black)
- ![HTML5](https://img.shields.io/badge/HTML5-blue?style=flat-square&logo=html5&logoColor=white)
- ![CSS3](https://img.shields.io/badge/CSS3-blue?style=flat-square&logo=css3&logoColor=white)
- ![Vercel](https://img.shields.io/badge/Vercel-black?style=flat-square&logo=vercel&logoColor=white)
- ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue?style=flat-square&logo=postgresql&logoColor=white)

## Installation
Follow these steps to get FileBridge up and running on your local machine:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kingsleyesisi/File_bridge.git
   cd File_bridge
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Linux/macOS
   venv\Scripts\activate.bat  # On Windows
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   - FileBridge uses PostgreSQL. Make sure you have it installed and running. 🐘
   - Update the `SQLALCHEMY_DATABASE_URI` in `app.py` with your PostgreSQL connection string.
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host:port/database_name'
   ```

5. **Set up environment variables:**
    - You may need to set the `SECRET_KEY` environment variable. If you don't the app will default to  `your-secret-key-change-this-in-production` in `app.py`.

6. **Run database migrations:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## Usage
1. **Run the application:**
   ```bash
   python app.py
   ```
   or
   ```bash
   python wsgi.py
   ```

2. **Open your browser and go to** `http://localhost:8000`.

3. **Start Sharing:**
   - Enter your name and a room name on the landing page.
   - Share the room name with others to collaborate.
   - Upload files using the paperclip icon.
   - Chat in real-time!

## Configuration
Here are some key configuration options you might want to tweak:

- **`SECRET_KEY`**: Used for session management.  **Important:** Change this in production!
  ```python
  app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
  ```

- **`SQLALCHEMY_DATABASE_URI`**: The database connection string. Update this to point to your PostgreSQL database.
  ```python
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://default:gN9Zeldkmb6P@ep-patient-bar-a49hhlnc-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require'
  ```

- **File Size Limit**: The maximum file size is set to 50MB. This can be adjusted in `app.py` and `app.js`.
  ```python
   max_size = 50 * 1024 * 1024  # 50MB
  ```

## Deployment

### Deploying to Vercel

FileBridge is designed to be easily deployed to Vercel. Here's how:

1.  **Create a Vercel account:** Sign up at [Vercel](https://vercel.com/).
2.  **Install the Vercel CLI:**

    ```bash
    npm install -g vercel
    ```
3.  **Deploy:**

    ```bash
    vercel
    ```

    Follow the prompts to link your project and deploy.  Make sure to set the environment variables in your Vercel project settings.

### Production Considerations
- **Use a production-ready WSGI server:** Gunicorn is included in the `requirements.txt`.
  ```bash
  gunicorn --bind 0.0.0.0:8000 wsgi:app
  ```
- **Set up a reverse proxy:** Use Nginx or Apache in front of your application for better performance and security.
- **Enable HTTPS:** Always use HTTPS in production.
- **Monitor your application:** Use tools like Sentry or New Relic to monitor your application for errors and performance issues.

## Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Here's how you can contribute:

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 📄

## Acknowledgments
- This project was built using open-source libraries. Thanks to the developers and maintainers of these tools!
- Special thanks to anyone who contributes to this project.

## Troubleshooting
- **Problem:**  `ModuleNotFoundError: No module named 'flask'`
  - **Solution:** Make sure you activated the virtual environment and installed the dependencies.
    ```bash
    source venv/bin/activate  # Or venv\Scripts\activate.bat on Windows
    pip install -r requirements.txt
    ```

- **Problem:** Database migrations failing.
  - **Solution:** Double-check your database connection string in `app.py`. Make sure the database server is running and accessible.

- **Problem:** SocketIO not connecting.
  - **Solution:** Ensure that your server allows WebSocket connections. Check your browser's console for any error messages.

- **Problem:** Files not uploading.
  - **Solution:** Make sure the file size is within the 50MB limit. Check the server logs for any file upload errors.

That's all for now! Happy sharing! 🎉

[![Built with DocMint](https://img.shields.io/badge/Generated%20by-DocMint-red)](https://github.com/kingsleyesisi/DocMint)