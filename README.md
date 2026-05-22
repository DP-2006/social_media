
<div align="center">

# 🧠 Social Network

<img src="https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white"/>
<img src="https://img.shields.io/badge/Ollama-0.1.8-000000?style=for-the-badge&logo=ollama&logoColor=white"/>
<img src="https://img.shields.io/badge/Qwen-7B-4A90E2?style=for-the-badge&logo=ai&logoColor=white"/>
<img src="https://img.shields.io/badge/WebSocket-00C7B7?style=for-the-badge&logo=socket.io&logoColor=white"/>
<img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>

<p align="center">
  <strong>Intelligent Social Network with AI-Powered Anonymous Chat Matching</strong>
  
<p align="center">
  <strong>An SAFA‑Inspired Network built with Django</strong>  
  <br><br>
  ⭐ <em>"Better than wen you see!"</em> ⭐
</p>

</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#project-structure">Structure</a> •
  <a href="#installation">Installation</a> •
  <a href="#api-endpoints">API</a> •
  <a href="#debug-log">Debug Log</a> •
  <a href="#upcoming-features">Coming Soon</a>
</p>

</div>

───────────────────────────────────────────────────────────────────────────────
📌 ABOUT SAFA
───────────────────────────────────────────────────────────────────────────────

Safa is a complete, production-ready backend for a modern social network. 
Built with Django Rest Framework and powered by Ollama AI, it delivers 
everything from OTP authentication to intelligent conversation starters.

> "Strong, scalable, and smart — just like your next big idea."


✨ FEATURES

| Category          | Capability                                      |
|-------------------|-------------------------------------------------|
| 👤 Authentication | OTP Registration/Login, JWT Tokens              |
| 📝 Posts          | Create, Edit, Delete, Like, Comment             |
| 🔍 Hashtags       | Advanced hashtag search                         |
| 🤖 AI Intelligence| Post & User analysis with Qwen 7B and gemma:27b |
| 📊 User Analytics | Behavior pattern recognition                    |
| ✅ Health Check   | Ollama & Database status                        |
| 💬 Direct Messages| Private chat between users                      |
| 🎭 Anonymous Chat | AI-powered partner matching (Coming Soon)       |
| 📸 Stories        | 24-hour ephemeral content                       |
| 🔒 Block System   | Two-way blocking                                |
| 🔍 Smart Search   | Users, posts, hashtags                          |

🏗️ PROJECT STRUCTURE

social_media-SAFA/
├── apps/
│   ├── accounts/          # OTP + JWT authentication
│   ├── profiles/          # User profiles & settings
│   ├── posts/             # Posts, likes, comments
│   ├── follows/           # Follow/unfollow system
│   ├── stories/           # 24-hour stories
│   ├── messaging/         # Direct messages
│   ├── hashtags/          # Hashtag management
│   ├── interactions/      # Explore feed
│   ├── blocks/            # Block system
│   ├── ml/                # Ollama AI integration
│   └── search/            # Smart search
├── core/                  # Base models & utilities
├── config/                # Django settings
├── media/                 # Uploaded files
├── static/                # Static files
├── manage.py
└── requirements.txt

🚀 INSTALLATION

Prerequisites:
- Python 3.10+
- PostgreSQL 16+ (or SQLite for development)
- Ollama (optional, for AI features)

Step-by-Step Setup:

1. Clone the repository
   git clone https://github.com/DP-2006/social_media-SAFA-.git
   cd social_media-SAFA-

2. Create virtual environment
   python -m venv venv

3. Activate virtual environment
   Windows:  venv\Scripts\activate
   Linux/Mac: source venv/bin/activate

4. Install dependencies
   pip install -r requirements.txt

5. Set up environment variables
   cp .env.example .env
   Edit .env with your settings

6. Run migrations
   python manage.py makemigrations
   python manage.py migrate

7. Create superuser (optional)
   python manage.py createsuperuser

8. Collect static files
   python manage.py collectstatic

9. Run the development server
   python manage.py runserver

Environment Variables (.env):

DEBUG=True
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/safa_db

Ollama Configuration:
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:27b
OLLAMA_ENABLED=True

Search Settings:
SEARCH_USE_OLLAMA=True

JWT Settings:
ACCESS_TOKEN_LIFETIME=5
REFRESH_TOKEN_LIFETIME=1




















# README Section

## Ollama AI Integration

### Model Installation

Install the desired model using Ollama. We currently recommend the **Qwen 2.7B** model.

> ⚠️ **Note:** You may encounter issues such as lack of image processing support with certain models.

### Configuration

To change the model or adjust additional settings:

1. Navigate to `app ml → service → ollama_client.py`
2. Modify the model and port settings as needed

For **hashtag** and **direct messaging** sections, follow the same approach in the `service` directory.

> ⚠️ **Important:** Ensure the required port is open in your firewall before running the application.

### Ollama Explore (Temporarily Disabled)

The Ollama Explore feature is currently **paused** due to server execution issues. To get started:

1. Go to the `serializer` in `ml` app
2. Enable `interaction service`

> 💡 **Note:** Services operate independently across all sections, making them reusable in other development projects. All existing apps will be updated accordingly in the near future.

### API Development

Python developers can write custom `serializers` and `views` to create API endpoints. This feature will be added by the development team soon.

> 🚀 **Good News:** The system works without Ollama Explore, which is great for enthusiasts who want to experiment!

### Database Support

This system supports **SQL** and **PostgreSQL** databases. Configuration is available in `config → setting`.

> ⚠️ **Note:** The current databases do not utilize a multi-tenant system. Please keep this in mind when referencing the codebase.

### AI Learning System

The system performs **gradual AI learning** through Ollama, albeit in a limited capacity. The goal is to leverage Ollama's capabilities effectively.

> ⚠️ **Important:** AI response quality depends entirely on the model and its training. **Do not rely solely on AI outputs** — errors are likely to occur!

---

## Contributing

We welcome suggestions, corrections, and feedback from all enthusiasts in this field. Your input is greatly appreciated! 🙏






















📡 API ENDPOINTS

Base URL: http://127.0.0.1:8000/api/

Authentication Header:
Authorization: Bearer <your_access_token>

🔐 ACCOUNTS (5 endpoints)


POST   /api/accounts/register/send-otp/     Send OTP for registration
POST   /api/accounts/register/verify/       Verify OTP & register
POST   /api/accounts/login/send-otp/        Send OTP for login
POST   /api/accounts/login/verify/          Verify OTP & get token
POST   /api/accounts/logout/                Logout user


👤 PROFILES (3 endpoints)


GET    /api/profiles/me/                    Get my profile
PATCH  /api/profiles/me/                    Update my profile
GET    /api/profiles/{user_id}/             Get user profile


📝 POSTS (11 endpoints)


GET    /api/posts/feed/                     Main feed
GET    /api/posts/explore/                  Explore feed (AI-powered)
GET    /api/posts/                          List all posts
POST   /api/posts/                          Create post
GET    /api/posts/{id}/                     Get post details
PATCH  /api/posts/{id}/                     Update post
DELETE /api/posts/{id}/                     Delete post
POST   /api/posts/{id}/like/                Like post
DELETE /api/posts/{id}/like/                Unlike post
POST   /api/posts/{id}/save/                Save post
GET    /api/posts/saved/                    Saved posts list


💬 COMMENTS (3 endpoints)


GET    /api/posts/{id}/comments/            Get comments
POST   /api/posts/{id}/comments/            Add comment
DELETE /api/posts/comments/{id}/            Delete comment


👥 FOLLOWS (4 endpoints)


POST   /api/follows/toggle/{user_id}/       Follow/Unfollow
GET    /api/follows/users/{id}/followers/   Followers list
GET    /api/follows/users/{id}/following/   Following list
GET    /api/follows/users/{id}/counts/      Follow stats


📸 STORIES (5 endpoints)

POST   /api/stories/                        Create story
GET    /api/stories/my/                     My stories
GET    /api/stories/following/              Following stories
POST   /api/stories/{id}/view/              Mark as viewed
DELETE /api/stories/{id}/delete/            Delete story


💌 MESSAGING (6 endpoints)


GET    /api/messages/conversations/         List conversations
POST   /api/messages/conversations/         Create conversation
GET    /api/messages/conversations/{id}/messages/ Get messages
POST   /api/messages/conversations/{id}/messages/ Send message
GET    /api/messages/analyze-target/{user_id}/ AI user analysis
GET    /api/messages/suggestions/opening/{user_id}/ AI message suggestions


🔍 SEARCH (5 endpoints)


GET    /api/search/?q={query}               Global search
GET    /api/search/user/@{username}/        Exact user search
GET    /api/search/users/?q={query}         Search users
GET    /api/search/posts/?q={query}         Search posts
GET    /api/search/hashtags/?q={query}      Search hashtags


🤖 AI/ML (4 endpoints)


GET    /api/ml/health/                      AI service health
GET    /api/ml/users/{id}/analyze/          Analyze user
GET    /api/ml/explore/                     AI recommendations
GET    /api/ml/recommended-hashtags/        Hashtag suggestions


🚫 BLOCKS (2 endpoints)


POST   /api/blocks/toggle/{user_id}/        Block/Unblock
GET    /api/blocks/blocked/                 Blocked users list


Total: 48 API Endpoints | 43 Require Authentication



🤖 AI INTEGRATION (OLLAMA)


Setup Ollama:

# Install Ollama (Linux/Mac)
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai/download (Windows)

# Pull the model
ollama pull gemma3:27b

# Or use Qwen for faster responses
ollama pull qwen:7b

# Run Ollama server
ollama serve

AI Features:

| Feature                 | Description                        | Fallback if Offline      |
|-------------------------|------------------------------------|--------------------------|
| Personality Analysis    | Analyzes user behavior patterns    | Basic profile stats      |
| Message Suggestions     | Smart opening lines for DMs        | Template-based           |
| Explore Feed            | Personalized content ranking       | Popularity-based         |
| Hashtag Recommendations | Trend-aware hashtags               | Static categories        |
| Content Moderation      | Auto-detect inappropriate content  | Basic keyword filter     |

Example AI Response:

{
  "analysis": {
    "personality_type": "Creative & Social",
    "engagement_pattern": "High evening activity",
    "interests": ["Technology", "Photography", "Music"],
    "suggested_connection": "Similar users with art interests"
  }
}

───────────────────────────────────────────────────────────────────────────────
🧪 TESTING
───────────────────────────────────────────────────────────────────────────────

Run Tests:

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts
python manage.py test apps.posts

# With coverage
pip install coverage
coverage run manage.py test
coverage report

Sample API Test (using curl):

# 1. Register
curl -X POST http://127.0.0.1:8000/api/accounts/register/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "09123456789"}'

# 2. Verify OTP
curl -X POST http://127.0.0.1:8000/api/accounts/register/verify/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "09123456789", "otp": "123456", "username": "alireza"}'

# Response contains access_token

# 3. Create post (using token)
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello Safa Network! 🚀"}'

# 4. Get feed
curl -X GET http://127.0.0.1:8000/api/posts/feed/ \
  -H "Authorization: Bearer YOUR_TOKEN"


🐛 DEBUG LOG & KNOWN ISSUES


Current Status:

| Issue                                      | Severity | Status                    |
|--------------------------------------------|----------|---------------------------|
| name 'user' is not defined in posts        | ⚠️ Warning| Non-blocking, being fixed |
| Static files collection warning            | ⚠️ Warning| Run 'collectstatic'       |
| Ollama connection on first run             | ℹ️ Info   | Auto-fallback works       |

Debug Commands:

# Check Ollama status
curl http://localhost:11434/api/tags

# Check API health
curl http://127.0.0.1:8000/api/ml/health/

# View Django logs
python manage.py runserver --verbosity 3

# Database shell
python manage.py dbshell


📊 DATABASE SCHEMA


Key Models:

User (Custom)
- phone (unique)
- username (unique)
- is_active
- is_private

Profile
- user (OneToOne)
- display_name
- bio
- avatar
- is_private

Post
- user (ForeignKey)
- content
- image
- likes_count
- comments_count
- created_at

Comment
- user (ForeignKey)
- post (ForeignKey)
- parent (ForeignKey, self)
- content

Follow
- follower (ForeignKey)
- following (ForeignKey)
- created_at

Story
- user (ForeignKey)
- media
- expires_at (24h later)

Conversation
- participants (ManyToMany)
- last_message

Message
- conversation (ForeignKey)
- sender (ForeignKey)
- content
- is_read

Note: All primary keys use UUID for security.


🎯 UPCOMING FEATURES


| Feature                           | Status        | ETA        |
|-----------------------------------|---------------|------------|
| 🔴 Anonymous Chat (AI Matching)   | In Development| Next Week  |
| 🟡 WebSocket Real-time Messages   | In Progress   | 2 Weeks    |
| 🟢 Push Notifications             | Planned       | 3 Weeks    |
| 🔵 Video Calls                    | Planned       | 1 Month    |
| 🟣 Group Chats Enhancement        | Planned       | 2 Weeks    |
| 🟠 Story Reactions                | Backlog       | -          |
| 🟤 Voice Messages                 | Backlog       | -          |

───────────────────────────────────────────────────────────────────────────────
🤝 CONTRIBUTING
───────────────────────────────────────────────────────────────────────────────

We love contributions!

# Fork the repository
# Create a feature branch
git checkout -b feature/awesome-feature

# Make your changes
# Run tests
python manage.py test

# Commit with conventional commit format
git commit -m "feat: add awesome feature"

# Push and create PR
git push origin feature/awesome-feature

Commit Convention:

feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Code style
refactor: Code refactor
test:     Testing
chore:    Maintenance

📄 LICENSE


MIT License - Free for personal and commercial use

Copyright (c) 2025 SAFA Network


👥 TEAM


GitHub: DP-2006

───────────────────────────────────────────────────────────────────────────────
📞 SUPPORT & CONTACT
───────────────────────────────────────────────────────────────────────────────

- GitHub Issues: https://github.com/DP-2006/social_media-SAFA-/issues
- Email: babkuand@gmail.com
-ID cart for donnate :
  5892-1012-2958-2614
  بانک سپه-دانیال پورمهدی
  sepah bank-Danil pourmehdi
<div align="center">



**⭐ If you like this project, give it a star! ⭐**

<sub>© 2026 SAFA - All rights reserved</sub>

</div>

═══════════════════════════════════════════════════════════════════════════════
                          END OF README
═══════════════════════════════════════════════════════════════════════════════