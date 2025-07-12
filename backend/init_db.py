#!/usr/bin/env python3
"""
Database initialization script for StackIt
Creates tables and populates with sample data
"""

from app import create_app
from models import db, User, Question, Answer, Tag, Vote, Notification
from datetime import datetime, timedelta

def init_database():
    app = create_app()
    
    with app.app_context():
        # Drop and recreate all tables
        print("Creating database tables...")
        db.drop_all()
        db.create_all()
        
        # Create sample users
        print("Creating sample users...")
        users = [
            User(username='john_doe', email='john@example.com', role='user', avatar='👨‍💻'),
            User(username='jane_smith', email='jane@example.com', role='admin', avatar='👩‍💼'),
            User(username='alex_dev', email='alex@example.com', role='user', avatar='👨‍🎨'),
            User(username='admin', email='admin@stackit.com', role='admin', avatar='⚡')
        ]
        
        # Set passwords
        for user in users:
            if user.username == 'admin':
                user.set_password('admin123')
            else:
                user.set_password('password123')
        
        db.session.add_all(users)
        db.session.commit()
        
        # Create sample tags
        print("Creating sample tags...")
        tags_data = [
            ('React', 'JavaScript library for building user interfaces'),
            ('JavaScript', 'Programming language for web development'),
            ('Python', 'High-level programming language'),
            ('Flask', 'Micro web framework for Python'),
            ('CSS', 'Cascading Style Sheets for styling'),
            ('HTML', 'HyperText Markup Language'),
            ('Node.js', 'JavaScript runtime environment'),
            ('JWT', 'JSON Web Tokens for authentication'),
            ('Authentication', 'User authentication and authorization'),
            ('Database', 'Data storage and management'),
            ('API', 'Application Programming Interface'),
            ('Design', 'User interface and experience design'),
            ('Responsive', 'Responsive web design'),
            ('Bootstrap', 'CSS framework'),
            ('Git', 'Version control system'),
        ]
        
        tags = []
        for tag_name, description in tags_data:
            tag = Tag(name=tag_name, description=description)
            tags.append(tag)
        
        db.session.add_all(tags)
        db.session.commit()
        
        # Create sample questions
        print("Creating sample questions...")
        questions_data = [
            {
                'title': 'How to implement JWT authentication in React?',
                'description': '''<p>I'm trying to implement JWT authentication in my React application. What's the best practice for storing tokens and handling authentication state?</p>
                
                <p>I've heard about storing tokens in localStorage, sessionStorage, or using httpOnly cookies. Which approach is most secure?</p>
                
                <p>Also, how do I handle token expiration and refresh tokens?</p>''',
                'author_id': 1,
                'tags': ['React', 'JWT', 'Authentication'],
                'views': 127
            },
            {
                'title': 'Best practices for responsive design in 2025?',
                'description': '''<p>What are the current best practices for creating responsive websites?</p>
                
                <p>Should I use CSS Grid, Flexbox, or a combination of both? What about mobile-first design?</p>
                
                <ul>
                <li>CSS Grid vs Flexbox</li>
                <li>Mobile-first approach</li>
                <li>Breakpoint strategies</li>
                <li>Image optimization</li>
                </ul>''',
                'author_id': 3,
                'tags': ['CSS', 'Responsive', 'Design'],
                'views': 89
            },
            {
                'title': 'How to handle CORS issues in Flask API?',
                'description': '''<p>I'm building a Flask API and my React frontend can't connect due to CORS errors.</p>
                
                <p>I've tried using Flask-CORS but still getting errors. Here's my current setup:</p>
                
                <pre><code>from flask_cors import CORS
app = Flask(_name_)
CORS(app)</code></pre>
                
                <p>What am I missing?</p>''',
                'author_id': 1,
                'tags': ['Flask', 'API', 'React'],
                'views': 156
            },
            {
                'title': 'Difference between useState and useReducer in React?',
                'description': '''<p>When should I use useState vs useReducer in React hooks?</p>
                
                <p>I understand useState is for simple state, but when does it make sense to switch to useReducer?</p>''',
                'author_id': 3,
                'tags': ['React', 'JavaScript'],
                'views': 203
            },
            {
                'title': 'How to optimize database queries in SQLAlchemy?',
                'description': '''<p>My Flask application is getting slow due to database queries. How can I optimize SQLAlchemy queries?</p>
                
                <p>I'm particularly concerned about N+1 queries and want to understand eager loading.</p>''',
                'author_id': 1,
                'tags': ['Python', 'Flask', 'Database'],
                'views': 145
            }
        ]
        
        questions = []
        for i, q_data in enumerate(questions_data):
            question = Question(
                title=q_data['title'],
                description=q_data['description'],
                author_id=q_data['author_id'],
                views=q_data['views'],
                created_at=datetime.utcnow() - timedelta(days=i+1)
            )
            
            # Add tags
            for tag_name in q_data['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    question.tags.append(tag)
            
            questions.append(question)
        
        db.session.add_all(questions)
        db.session.commit()
        
        # Create sample answers
        print("Creating sample answers...")
        answers_data = [
            {
                'content': '''<p>You can store JWT tokens in memory or httpOnly cookies. Here's a comprehensive approach:</p>
                
                <ol>
                <li><strong>Store tokens in memory</strong> - Most secure but doesn't persist across page refreshes</li>
                <li><strong>Use refresh tokens</strong> - Store refresh token in httpOnly cookie, access token in memory</li>
                <li><strong>Implement auto-logout</strong> on token expiry</li>
                </ol>
                
                <p>Here's a basic implementation:</p>
                
                <pre><code>// Auth context
const AuthContext = createContext();

export const useAuth = () => {
  const [token, setToken] = useState(null);
  
  const login = async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    setToken(response.data.access_token);
  };
  
  return { token, login };
};</code></pre>''',
                'author_id': 2,
                'question_id': 1,
                'is_accepted': True
            },
            {
                'content': '''<p>I'd recommend using a state management library like Redux or Context API to handle authentication state globally.</p>
                
                <p>This way you can easily check authentication status across your entire app.</p>''',
                'author_id': 3,
                'question_id': 1,
                'is_accepted': False
            },
            {
                'content': '''<p>For responsive design in 2025, I recommend this approach:</p>
                
                <ol>
                <li><strong>Mobile-first design</strong> - Start with mobile styles and enhance for larger screens</li>
                <li><strong>CSS Grid for layouts</strong> - Use for page-level layouts and complex grid systems</li>
                <li><strong>Flexbox for components</strong> - Perfect for aligning items and distributing space</li>
                <li><strong>Container queries</strong> - The new responsive design tool for component-based layouts</li>
                </ol>
                
                <p>Example breakpoints:</p>
                
                <pre><code>/* Mobile first */
.container {
  width: 100%;
  padding: 1rem;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    max-width: 768px;
    margin: 0 auto;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    max-width: 1024px;
    padding: 2rem;
  }
}</code></pre>''',
                'author_id': 2,
                'question_id': 2,
                'is_accepted': True
            },
            {
                'content': '''<p>The CORS issue is likely due to missing configuration. Try this:</p>
                
                <pre><code>from flask_cors import CORS

app = Flask(_name_)

# Configure CORS properly
CORS(app, origins=['http://localhost:3000'], 
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Also make sure to handle preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = Response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response</code></pre>''',
                'author_id': 2,
                'question_id': 3,
                'is_accepted': True
            }
        ]
        
        answers = []
        for a_data in answers_data:
            answer = Answer(
                content=a_data['content'],
                author_id=a_data['author_id'],
                question_id=a_data['question_id'],
                is_accepted=a_data['is_accepted'],
                created_at=datetime.utcnow() - timedelta(hours=len(answers))
            )
            answers.append(answer)
        
        db.session.add_all(answers)
        db.session.commit()
        
        # Create sample votes
        print("Creating sample votes...")
        votes_data = [
            {'user_id': 1, 'question_id': 1, 'value': 1},
            {'user_id': 2, 'question_id': 1, 'value': 1},
            {'user_id': 3, 'question_id': 1, 'value': 1},
            {'user_id': 1, 'question_id': 2, 'value': 1},
            {'user_id': 2, 'question_id': 2, 'value': 1},
            {'user_id': 1, 'answer_id': 1, 'value': 1},
            {'user_id': 3, 'answer_id': 1, 'value': 1},
            {'user_id': 2, 'answer_id': 2, 'value': 1},
        ]
        
        votes = []
        for v_data in votes_data:
            vote = Vote(**v_data)
            votes.append(vote)
        
        db.session.add_all(votes)
        db.session.commit()
        
        # Create sample notifications
        print("Creating sample notifications...")
        notifications_data = [
            {
                'user_id': 1,
                'type': 'answer',
                'message': 'Jane Smith answered your question about JWT authentication',
                'data': {'question_id': 1, 'answer_id': 1},
                'is_read': False
            },
            {
                'user_id': 1,
                'type': 'vote',
                'message': 'Your question received 3 upvotes',
                'data': {'question_id': 1},
                'is_read': False
            },
            {
                'user_id': 3,
                'type': 'answer',
                'message': 'Jane Smith answered your question about responsive design',
                'data': {'question_id': 2, 'answer_id': 3},
                'is_read': True
            }
        ]
        
        notifications = []
        for n_data in notifications_data:
            notification = Notification(
                user_id=n_data['user_id'],
                type=n_data['type'],
                message=n_data['message'],
                data=n_data['data'],
                is_read=n_data['is_read'],
                created_at=datetime.utcnow() - timedelta(hours=len(notifications))
            )
            notifications.append(notification)
        
        db.session.add_all(notifications)
        db.session.commit()
        
        print("\n✅ Database initialized successfully!")
        print("\n📊 Sample data created:")
        print(f"   👥 Users: {User.query.count()}")
        print(f"   ❓ Questions: {Question.query.count()}")
        print(f"   💬 Answers: {Answer.query.count()}")
        print(f"   🏷  Tags: {Tag.query.count()}")
        print(f"   👍 Votes: {Vote.query.count()}")
        print(f"   🔔 Notifications: {Notification.query.count()}")
        
        print("\n🔐 Test accounts:")
        print("   Admin: admin / admin123")
        print("   User:  john_doe / password123")
        print("   User:  jane_smith / password123")
        print("   User:  alex_dev / password123")

if __name__ == '__main__':
    init_database()