# Brand Bloom - AI Business Toolkit

A comprehensive AI-powered business toolkit designed to help small and medium businesses leverage artificial intelligence for website creation, email marketing, feedback analysis, sales insights, and more.

## 🌟 Features

### Core AI Tools
- **🌐 Website Builder**: Generate professional, responsive websites with AI-powered content
- **📧 Email Drafter & Sender**: Create and send professional emails with bulk sending capabilities
- **💬 Feedback Analyzer**: Analyze customer feedback using advanced sentiment analysis
- **🎨 Poster Maker**: Design marketing materials and promotional posters
- **📊 Sales Insights**: Upload CSV data to get comprehensive sales analytics and forecasting

### Advanced Features
- **🎤 Voice Commands**: Control the entire platform using speech-to-text integration
- **🌍 Multi-language Support**: Built-in Google Translate integration
- **📱 Responsive Design**: Mobile-first approach with modern UI/UX
- **🔐 User Authentication**: Secure login/registration system with session management
- **💾 Database Integration**: SQLite database for storing user data, websites, and feedback

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLite** - Database for data persistence
- **Google Gemini AI** - AI content generation
- **Pandas & NumPy** - Data analysis and processing

### Frontend
- **Bootstrap 5** - Responsive UI framework
- **Vanilla JavaScript** - Interactive functionality
- **Google Fonts** - Typography (Inter, Roboto, Open Sans)
- **Font Awesome** - Icons and visual elements

### AI Integration
- **Google Generative AI (Gemini)** - Content generation
- **Speech Recognition API** - Voice command processing
- **Natural Language Processing** - Feedback sentiment analysis

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/brand-bloom-ai-toolkit.git
cd brand-bloom-ai-toolkit
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-google-gemini-api-key
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
AI_MODEL=gemini
AI_MAX_TOKENS=1500
AI_TEMPERATURE=0.7
```

### Step 5: Initialize Database
```bash
python database.py
```

### Step 6: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5003`

## 📋 API Keys Setup

### Google Gemini AI API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### Email Configuration (Gmail)
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Add your email and app password to `.env`

## 🏗️ Project Structure

```
brand-bloom-ai-toolkit/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── database.py                 # Database models and operations
├── speech_processor.py         # Speech-to-text integration
├── requirements.txt            # Python dependencies
├── uploads/                    # File upload directory
├── modules/
│   └── ai_tools/
│       ├── website_builder.py  # Website generation logic
│       ├── email_drafter.py    # Email creation logic
│       ├── feedback_analyzer.py # Sentiment analysis
│       ├── poster_maker.py     # Poster generation
│       └── sales_insights.py   # Sales data analysis
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── dashboard.html         # Main dashboard
│   ├── profile.html           # User profile management
│   ├── settings.html          # Application settings
│   ├── onboarding.html        # Business setup flow
│   ├── login.html & register.html # Authentication
│   └── tools/
│       ├── website.html       # Website builder interface
│       ├── email.html         # Email tool interface
│       ├── feedback.html      # Feedback analyzer
│       ├── poster.html        # Poster maker
│       └── sales.html         # Sales insights
└── static/
    ├── css/                   # Custom stylesheets
    ├── js/                    # JavaScript modules
    └── images/                # Static assets
```

## 🎯 Usage Guide

### 1. Account Setup
1. Register a new account or login
2. Complete the business onboarding process
3. Configure your business information in the profile

### 2. Website Builder
- Select website type (business, portfolio, e-commerce, etc.)
- Provide business details and preferences
- Generate AI-powered website content
- Deploy with custom keywords
- Collect customer feedback through integrated forms

### 3. Email Marketing
- Choose email type and tone
- Configure recipient details
- Generate professional email content
- Send individual or bulk emails via CSV upload

### 4. Feedback Analysis
- Input customer feedback manually
- Analyze stored feedback from websites
- Get sentiment analysis, key insights, and emotional analysis
- View trends and patterns in customer sentiment

### 5. Sales Analytics
- Upload CSV files with sales data
- Get comprehensive analytics including:
  - Sales trends and forecasting
  - Product performance analysis
  - Customer behavior insights
  - Time-based patterns
  - Actionable recommendations

### 6. Voice Commands
Use speech-to-text for hands-free operation:
- "Create a website for my restaurant"
- "Generate a marketing email"
- "Analyze this feedback: [speak feedback]"
- "Make a poster for sale event"

## 🔧 Configuration Options

### AI Model Settings
```python
AI_MODEL = 'gemini'  # AI provider
AI_MAX_TOKENS = 1500  # Maximum response length
AI_TEMPERATURE = 0.7  # Creativity level (0.0-1.0)
```

### Database Configuration
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///ai_toolkit.db'
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB file limit
```

## 🚦 API Endpoints

### Website Management
- `POST /api/generate-website` - Generate new website
- `GET /api/get-user-websites` - List user websites
- `POST /api/deploy-website` - Deploy website with keyword
- `DELETE /api/delete-website/<id>` - Delete website

### Feedback System
- `POST /api/submit-feedback` - Submit customer feedback
- `POST /api/analyze-feedback` - Analyze feedback text
- `GET /api/get-all-feedback` - Get user feedback

### Email Tools
- `POST /api/draft-email` - Generate email content
- `POST /api/send-email` - Send single email
- `POST /api/send-bulk-emails` - Send bulk emails

### Sales Analytics
- `POST /api/upload-sales` - Upload sales data
- `GET /api/sales-insights` - Get analytics results

### Speech Processing
- `POST /api/process-speech` - Process voice commands
- `GET /api/speech-capabilities` - Get speech features

## 🎨 Design System

### Color Palette
- **Primary Ivory**: #F5F5DC (Backgrounds)
- **Secondary Red**: #DC143C (Accents, CTAs)
- **Text Dark**: #2C2C2C (Primary text)
- **Text Light**: #6B6B6B (Secondary text)

### Typography
- **Headings**: Roboto (Google Fonts)
- **Body Text**: Inter (Google Fonts)
- **Responsive**: Mobile-first design approach

## 🧪 Testing

### Manual Testing
1. Test all AI tools with various inputs
2. Verify user authentication flows
3. Test website deployment and feedback collection
4. Validate email sending functionality
5. Check speech recognition accuracy

### Data Testing
- Test CSV uploads with different formats
- Verify database operations
- Test API endpoints with various payloads

## 🚀 Deployment

### Local Development
```bash
python app.py
# Runs on http://localhost:5003 with debug mode
```

### Production Deployment
1. Set `DEBUG=False` in config
2. Use production WSGI server (Gunicorn, uWSGI)
3. Configure environment variables
4. Set up reverse proxy (Nginx)
5. Enable HTTPS/SSL

### Environment Variables for Production
```env
FLASK_ENV=production
SECRET_KEY=strong-production-secret-key
GEMINI_API_KEY=production-api-key
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Test new features thoroughly
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced language model capabilities
- **Bootstrap** for responsive UI components
- **Font Awesome** for comprehensive icon library
- **Flask** community for excellent documentation
- **Open source contributors** who made this project possible

## 📞 Support

For support, questions, or feature requests:
- Create an issue on GitHub
- Email: support@brandbloom.ai
- Documentation: [Wiki](https://github.com/yourusername/brand-bloom-ai-toolkit/wiki)

## 🔄 Changelog

### Version 1.0.0 (Current)
- Initial release with core AI tools
- Speech-to-text integration
- Multi-language support
- Comprehensive dashboard
- Email marketing system
- Sales analytics platform

### Planned Features
- **v1.1.0**: Advanced analytics dashboard
- **v1.2.0**: Integration with social media platforms
- **v1.3.0**: Mobile app companion
- **v2.0.0**: Enterprise features and team collaboration

---

**Made with ❤️ for small businesses worldwide**
