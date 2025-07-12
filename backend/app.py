from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from sqlalchemy import or_, and_, desc, asc
from datetime import datetime
import os

from config import config
from models import db, User, Question, Answer, Vote, Tag, Notification, question_tags
from auth import (
    admin_required, get_current_user, sanitize_html, create_notification,
    login_user, register_user
)

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Auth Routes
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        if not data or not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        result, error = register_user(data['username'], data['email'], data['password'])
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify(result), 201
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        print(data)
        if not data or not all(k in data for k in ('username', 'password')):
            return jsonify({'error': 'Username/email and password are required'}), 400
        
        result, error = login_user(data['username'], data['password'])
        
        if error:
            return jsonify({'error': error}), 401
        
        return jsonify(result), 200
    
    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required()
    def get_current_user_info():
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': current_user.to_dict()}), 200
    
    # Question Routes
    @app.route('/api/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '')
        tags = request.args.getlist('tags')
        sort_by = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')
        
        # Base query
        query = Question.query.filter_by(is_active=True)
        
        # Search filter
        if search:
            query = query.filter(
                or_(
                    Question.title.contains(search),
                    Question.description.contains(search)
                )
            )
        
        # Tags filter
        if tags:
            tag_objects = Tag.query.filter(Tag.name.in_(tags)).all()
            if tag_objects:
                query = query.filter(
                    Question.tags.any(Tag.id.in_([tag.id for tag in tag_objects]))
                )
        
        # Sorting
        if sort_by == 'votes':
            # Sort by vote score (this is a simplified version)
            if order == 'desc':
                query = query.order_by(desc(Question.created_at))  # Placeholder
            else:
                query = query.order_by(asc(Question.created_at))   # Placeholder
        elif sort_by == 'views':
            if order == 'desc':
                query = query.order_by(desc(Question.views))
            else:
                query = query.order_by(asc(Question.views))
        else:  # created_at
            if order == 'desc':
                query = query.order_by(desc(Question.created_at))
            else:
                query = query.order_by(asc(Question.created_at))
        
        # Paginate
        questions = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'questions': [q.to_dict() for q in questions.items],
            'total': questions.total,
            'pages': questions.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    @app.route('/api/questions/<int:question_id>', methods=['GET'])
    def get_question(question_id):
        question = Question.query.get_or_404(question_id)
        
        if not question.is_active:
            return jsonify({'error': 'Question not found'}), 404
        
        # Increment view count
        question.views += 1
        db.session.commit()
        
        return jsonify(question.to_dict(include_answers=True)), 200
    
    @app.route('/api/questions', methods=['POST'])
    @jwt_required()
    def create_question():
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ('title', 'description', 'tags')):
            return jsonify({'error': 'Title, description, and tags are required'}), 400
        
        # Sanitize HTML content
        title = data['title'].strip()
        description = sanitize_html(data['description'])
        
        if not title or not description:
            return jsonify({'error': 'Title and description cannot be empty'}), 400
        
        # Create question
        question = Question(
            title=title,
            description=description,
            author_id=current_user.id
        )
        
        # Handle tags
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            question.tags.append(tag)
        
        db.session.add(question)
        try:
            db.session.commit()
            return jsonify(question.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create question'}), 500
    
    @app.route('/api/questions/<int:question_id>', methods=['PUT'])
    @jwt_required()
    def update_question(question_id):
        current_user = get_current_user()
        question = Question.query.get_or_404(question_id)
        
        if question.author_id != current_user.id and current_user.role != 'admin':
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            question.title = data['title'].strip()
        if 'description' in data:
            question.description = sanitize_html(data['description'])
        if 'tags' in data:
            question.tags.clear()
            for tag_name in data['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                question.tags.append(tag)
        
        question.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return jsonify(question.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update question'}), 500
    
    @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
    @jwt_required()
    def delete_question(question_id):
        current_user = get_current_user()
        question = Question.query.get_or_404(question_id)
        
        if question.author_id != current_user.id and current_user.role != 'admin':
            return jsonify({'error': 'Permission denied'}), 403
        
        question.is_active = False
        try:
            db.session.commit()
            return jsonify({'message': 'Question deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete question'}), 500
    
    # Answer Routes
    @app.route('/api/questions/<int:question_id>/answers', methods=['POST'])
    @jwt_required()
    def create_answer(question_id):
        current_user = get_current_user()
        question = Question.query.get_or_404(question_id)
        
        if not question.is_active:
            return jsonify({'error': 'Question not found'}), 404
        
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
        
        content = sanitize_html(data['content'])
        if not content:
            return jsonify({'error': 'Content cannot be empty'}), 400
        
        answer = Answer(
            content=content,
            author_id=current_user.id,
            question_id=question_id
        )
        
        db.session.add(answer)
        
        try:
            db.session.commit()
            
            # Create notification for question author
            if question.author_id != current_user.id:
                create_notification(
                    user_id=question.author_id,
                    notification_type='answer',
                    message=f'{current_user.username} answered your question: {question.title}',
                    data={'question_id': question_id, 'answer_id': answer.id}
                )
            
            return jsonify(answer.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create answer'}), 500
    
    @app.route('/api/answers/<int:answer_id>', methods=['PUT'])
    @jwt_required()
    def update_answer(answer_id):
        current_user = get_current_user()
        answer = Answer.query.get_or_404(answer_id)
        
        if answer.author_id != current_user.id and current_user.role != 'admin':
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        
        if 'content' in data:
            answer.content = sanitize_html(data['content'])
            answer.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return jsonify(answer.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update answer'}), 500
    
    @app.route('/api/answers/<int:answer_id>/accept', methods=['POST'])
    @jwt_required()
    def accept_answer(answer_id):
        current_user = get_current_user()
        answer = Answer.query.get_or_404(answer_id)
        question = answer.question
        
        if question.author_id != current_user.id:
            return jsonify({'error': 'Only question author can accept answers'}), 403
        
        # Remove acceptance from other answers
        for other_answer in question.answers:
            other_answer.is_accepted = False
        
        # Accept this answer
        answer.is_accepted = True
        
        try:
            db.session.commit()
            
            # Create notification for answer author
            if answer.author_id != current_user.id:
                create_notification(
                    user_id=answer.author_id,
                    notification_type='accept',
                    message=f'Your answer was accepted for: {question.title}',
                    data={'question_id': question.id, 'answer_id': answer.id}
                )
            
            return jsonify(answer.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to accept answer'}), 500
    
    # Voting Routes
    @app.route('/api/questions/<int:question_id>/vote', methods=['POST'])
    @jwt_required()
    def vote_question(question_id):
        current_user = get_current_user()
        question = Question.query.get_or_404(question_id)
        
        data = request.get_json()
        if not data or 'value' not in data or data['value'] not in [-1, 0, 1]:
            return jsonify({'error': 'Vote value must be -1, 0, or 1'}), 400
        
        vote_value = data['value']
        
        # Find existing vote
        existing_vote = Vote.query.filter_by(
            user_id=current_user.id,
            question_id=question_id
        ).first()
        
        if vote_value == 0:
            # Remove vote
            if existing_vote:
                db.session.delete(existing_vote)
        else:
            if existing_vote:
                # Update existing vote
                existing_vote.value = vote_value
            else:
                # Create new vote
                vote = Vote(
                    user_id=current_user.id,
                    question_id=question_id,
                    value=vote_value
                )
                db.session.add(vote)
        
        try:
            db.session.commit()
            return jsonify({
                'vote_score': question.get_vote_score(),
                'user_vote': vote_value
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to vote'}), 500
    
    @app.route('/api/answers/<int:answer_id>/vote', methods=['POST'])
    @jwt_required()
    def vote_answer(answer_id):
        current_user = get_current_user()
        answer = Answer.query.get_or_404(answer_id)

        data = request.get_json()
        if not data or 'vote' not in data or data['vote'] not in ['up', 'down', 'remove']:
            return jsonify({'error': 'Vote must be "up", "down", or "remove"'}), 400

        vote_type = data['vote']
        vote_value = 1 if vote_type == 'up' else 0  # down/remove treated the same for now

        existing_vote = Vote.query.filter_by(
            user_id=current_user.id,
            answer_id=answer_id
        ).first()

        if vote_type == 'remove':
            if existing_vote:
                db.session.delete(existing_vote)
        else:
            if existing_vote:
                existing_vote.value = vote_value
            else:
                new_vote = Vote(
                    user_id=current_user.id,
                    answer_id=answer_id,
                    value=vote_value
                )
                db.session.add(new_vote)

        try:
            db.session.commit()
            return jsonify({
                'vote_score': answer.get_vote_score(),
                'user_vote': vote_value
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to vote'}), 500

    
    # Tag Routes
    @app.route('/api/tags', methods=['GET'])
    def get_tags():
        search = request.args.get('search', '')
        limit = min(request.args.get('limit', 50, type=int), 100)
        
        query = Tag.query
        if search:
            query = query.filter(Tag.name.contains(search))
        
        tags = query.limit(limit).all()
        return jsonify([tag.to_dict() for tag in tags]), 200
    
    # Notification Routes
    @app.route('/api/notifications', methods=['GET'])
    @jwt_required()
    def get_notifications():
        current_user = get_current_user()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        notifications = Notification.query.filter_by(user_id=current_user.id)\
            .order_by(desc(Notification.created_at))\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'notifications': [n.to_dict() for n in notifications.items],
            'total': notifications.total,
            'unread_count': Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        }), 200
    
    @app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
    @jwt_required()
    def mark_notification_read(notification_id):
        current_user = get_current_user()
        notification = Notification.query.filter_by(
            id=notification_id, user_id=current_user.id
        ).first_or_404()
        
        notification.is_read = True
        
        try:
            db.session.commit()
            return jsonify(notification.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to mark notification as read'}), 500
    
    @app.route('/api/notifications/read-all', methods=['POST'])
    @jwt_required()
    def mark_all_notifications_read():
        current_user = get_current_user()
        
        Notification.query.filter_by(user_id=current_user.id, is_read=False)\
            .update({'is_read': True})
        
        try:
            db.session.commit()
            return jsonify({'message': 'All notifications marked as read'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to mark notifications as read'}), 500
    
    # Admin Routes
    @app.route('/api/admin/users', methods=['GET'])
    @admin_required
    def admin_get_users():
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        users = User.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [u.to_dict() for u in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
    
    @app.route('/api/admin/users/<int:user_id>/ban', methods=['POST'])
    @admin_required
    def admin_ban_user(user_id):
        user = User.query.get_or_404(user_id)
        user.is_active = False
        
        try:
            db.session.commit()
            return jsonify({'message': 'User banned successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to ban user'}), 500
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        db.create_all()
        
        # Create default admin user if doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@stackit.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Created default admin user: admin/admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)