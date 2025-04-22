# Django Expense Tracker

A comprehensive web application for tracking and managing personal or business expenses, built with Django and enhanced with AI capabilities.

## 🌟 Features

### Core Functionality
- **Expense Management**: Add, edit, delete, and categorize expenses
- **Budget Planning**: Set and track budgets for different expense categories
- **Reports & Analytics**: Visual representation of spending patterns
- **Categories & Tags**: Organize expenses with custom categories and tags
- **Receipt Storage**: Upload and store receipt images with expenses
- **Export Options**: Download expense reports as PDF, CSV, or Excel

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dashboard**: Overview of recent activities and financial status
- **Multi-currency Support**: Track expenses in different currencies
- **Recurring Expenses**: Set up automated entries for regular payments

### Security & Authentication
- **User Authentication**: Secure login and registration system
- **Google OAuth Integration**: Sign in with Google accounts
- **Role-based Access**: Different permission levels for users
- **Data Encryption**: Secure storage of sensitive information

### AI-Powered Assistant
- **Conversational Interface**: Chat with AI to manage expenses
- **Natural Language Processing**: Add expenses using everyday language
- **Spending Insights**: Get AI-generated insights about spending habits
- **Expense Recommendations**: Receive suggestions for budget optimization

## 🚀 Setup & Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/django-expense-tracker.git
   cd django-expense-tracker
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   ```

3. Activate the virtual environment
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the root directory with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_database_url
   GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
   GOOGLE_OAUTH_SECRET=your_google_secret
   GEMINI_API_KEY=your_gemini_api_key
   ```

6. Run migrations
   ```
   python manage.py migrate
   ```

7. Create a superuser
   ```
   python manage.py createsuperuser
   ```

8. Start the development server
   ```
   python manage.py runserver
   ```

## 🤖 AI Chatbot Integration (vision)

The application includes a chatbot that allows users to interact with the expense tracker using natural language:

- Add new expenses through natural language
- Query past expenses and spending patterns
- Get budget recommendations and insights
- Generate reports and summaries

### Current Implementation

The chatbot currently uses a pattern-based intent recognition system:

1. **Intent Detection**: Identifies user intent by matching keywords and phrases
2. **Information Extraction**: Pulls relevant details from the user message using regex patterns
3. **API Integration**: Connects with the expense tracking API to perform actions

The pattern-based system provides reliable functionality for basic expense operations and serves as the foundation for more advanced AI features.

### Gemini Integration Attempt

We have also explored integrating Google's Gemini Pro model to enhance our chatbot capabilities. While this code is preserved in the codebase, it is currently disabled due to several challenges:

1. **Function Calling Limitations**: Gemini Pro's function calling capabilities were less mature than expected, requiring additional workarounds.
   
2. **Context Window Constraints**: We faced difficulties maintaining conversation context for complex financial discussions.
   
3. **Fine-tuning Restrictions**: Unlike some other models, Gemini Pro doesn't currently support fine-tuning for domain-specific knowledge, limiting our ability to train it on financial terminology.
   
4. **Response Consistency**: Ensuring consistent formatting of financial data in responses required extensive prompt engineering.

## 🧪 Testing

Run the test suite with:
```
python manage.py test
```

For testing the Gemini integration specifically:
```
python chatbot/test_gemini_client.py
```

## 🔮 Future Plans

- Enhanced data visualization with interactive charts
- Mobile application using the existing API
- Advanced AI features for predictive budgeting
- Integration with banking APIs for automatic expense tracking
- Multi-user expense sharing and splitting

## 🛠️ Technologies Used

- **Backend**: Django 4.2, Python 3.8+
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Authentication**: Django-Allauth, OAuth
- **API**: Django REST Framework
- **AI**: Pattern-based NLP (current), Google Gemini Pro (future)
- **Deployment**: Heroku, Docker
