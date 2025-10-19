# 🤖 QaderiChat — AI Chatbot with Django & OpenAI

QaderiChat is a **modern, visionary, and responsive AI chatbot** built with Django and integrated with OpenAI’s ChatGPT API (and optionally Anthropic Claude).  
It provides a **crystal-clear, futuristic UI**, smooth chat experience with real-time messaging, live typing indicators, and full dark/light theme support.

![QaderiChat UI](./static/images/banner.png)

---

## ✨ Key Features

- 🤖 **Dual AI Engine** — Switch between OpenAI’s ChatGPT or Anthropic Claude seamlessly  
- 💬 **Real-time Messaging** — Smooth chat flow with live typing indicators  
- 🌓 **Dark & Light Theme** — Persistent theme with one-click toggle  
- 📜 **Session-based History** — Navigate and restore previous conversations  
- 📱 **Fully Responsive** — Optimized for desktop, tablet, and mobile devices  
- 🧠 **Advanced UI/UX** — Sidebar navigation, modern animations, and minimal UI  
- 🔐 **Secure Sessions** — Session-key–based isolation for every user  
- 🧪 **Tested & Scalable** — Ready for production with WebSocket support  
- 🚀 **Extensible Architecture** — Supports multiple AI backends and configurations

---

## 🧰 Tech Stack

**Frontend:**  
- HTML5, CSS3, JavaScript (ES6+)  
- Bootstrap 5  
- Font Awesome 6  

**Backend:**  
- Django 5+ (Python 3.11+)  
- Django ORM, Django Channels (WebSocket support)  
- Session & CSRF protection  

**AI Providers:**  
- OpenAI API (ChatGPT)  
- Anthropic API (Claude) *(optional)*  

**Database:**  
- SQLite (development)  
- PostgreSQL (production ready)

---

## ⚡ Quick Start Guide

### ✅ Prerequisites

- Python 3.8 or higher  
- pip (Python package manager)  
- OpenAI or Anthropic API Key  

---

### 📥 1. Clone the Repository
```bash
git clone https://github.com/your-username/QaderiChat.git
cd QaderiChat
🐍 2. Create and Activate a Virtual Environment
bash
Copy code
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
📦 3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
⚙️ 4. Configure Environment Variables
Create a .env file in the project root:

env
Copy code
# Choose one AI Provider
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here

AI_PROVIDER=openai  # or claude

# Django
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
(Optional: you can copy from .env.example if provided.)

🧭 5. Run Database Migrations
bash
Copy code
python manage.py makemigrations
python manage.py migrate
👤 6. Create a Superuser (Optional)
bash
Copy code
python manage.py createsuperuser
🧹 7. Collect Static Files
bash
Copy code
python manage.py collectstatic
🚀 8. Start the Development Server
bash
Copy code
python manage.py runserver
Visit 👉 http://127.0.0.1:8000 to chat with QaderiChat.

🧠 Configuration
All chatbot settings can be adjusted in the Django Admin Panel:

arduino
Copy code
http://127.0.0.1:8000/admin
🧠 Model name (e.g., gpt-3.5-turbo, gpt-4, Claude)

🧮 Max tokens

🔥 Temperature

📜 System prompt

⚡ Enable/Disable provider

🌐 API Endpoints
Endpoint	Method	Description
/	GET	Landing page with intro UI
/chat/	GET	Main chatbot interface
/api/send-message/	POST	Send user message to AI
/api/get-messages/	GET	Get messages for the active session
/api/get-sessions/	GET	List all previous sessions
/api/get-session-messages/<uuid:id>/	GET	Load messages for a specific session
/api/clear-chat/	POST	Clear the current chat session
/api/test/	GET	Test API configuration

🧪 Testing
Run the test suite:

bash
Copy code
python manage.py test
Run individual test modules:

bash
Copy code
python manage.py test chat.tests.ChatModelsTestCase
python manage.py test chat.tests.ChatServiceTestCase
python manage.py test chat.tests.ChatViewsTestCase
📦 Deployment Guide
🔐 Production Settings
Set DEBUG=False in .env

Use PostgreSQL for the database

Set proper ALLOWED_HOSTS

Configure static files (e.g., with WhiteNoise or CDN)

Set up Redis for WebSockets (optional)

🐳 Docker (Optional)
You can containerize the app for deployment with Docker:

bash
Copy code
docker build -t qaderichat .
docker run -p 8000:8000 qaderichat
🧑‍💻 Developer
👨‍💻 Name: Faridullah Qaderi
🏢 Organization: MCIT - Afghanistan
📧 Email: faridullah.qaderi@mcit.gov.af
📞 Phone: +93 788 70 74 79

Faridullah Qaderi is a passionate software engineer focused on AI integration, full-stack development, and building visionary digital platforms that blend technology with real human experiences.

🤝 Contributing
Contributions are welcome!

Fork the repo

Create a new branch

Add your feature or fix

Commit and push

Submit a Pull Request 🎉

🪪 License
This project is licensed under the MIT License.

kotlin
Copy code
MIT License
Copyright (c) 2025
Permission is hereby granted, free of charge, to any person obtaining a copy of this software...
🙏 Acknowledgments
🧠 OpenAI & Anthropic for powerful AI APIs

🕸️ Django community for a rock-solid backend

💻 Bootstrap & Font Awesome for modern UI components

🫡 MCIT-AF for supporting innovative AI projects

🧑‍💻 Faridullah Qaderi — Lead Developer of QaderiChat

⭐ Star this repository if you find it useful!
Made with ❤️ in Afghanistan 🇦🇫