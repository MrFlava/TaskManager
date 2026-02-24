from flask import Blueprint, jsonify, request
from app.models import db, User

# Create Blueprint for user routes
users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET', 'POST'])
def users():
    """List all users or create a new user"""
    if request.method == 'GET':
        """List all users"""
        try:
            users = User.query.all()
            return jsonify({
                'status': 'success',
                'count': len(users),
                'users': [user.to_dict() for user in users]
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    elif request.method == 'POST':
        """Create a new user"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data or not all(k in data for k in ['name', 'email', 'password']):
                return jsonify({
                    'status': 'error',
                    'message': 'Missing required fields: name, email, password'
                }), 400
            
            # Check for duplicate email
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({
                    'status': 'error',
                    'message': 'Email already exists'
                }), 400
            
            # Create new user
            user = User(
                name=data['name'],
                email=data['email'],
                password=data['password']
            )
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'User created successfully',
                'user': user.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500


@users_bp.route('/<int:user_id>/', methods=['GET', 'PATCH', 'DELETE'])
def user_by_id(user_id):
    """Get, update, or delete a specific user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        """Get user by ID"""
        try:
            return jsonify({
                'status': 'success',
                'user': user.to_dict()
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    elif request.method == 'PATCH':
        """Update user (partial update allowed)"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'No data provided'
                }), 400
            
            # Partial update - only update provided fields
            if 'name' in data:
                user.name = data['name']
            
            if 'email' in data:
                # Check for duplicate email (excluding current user)
                existing_user = User.query.filter(
                    User.email == data['email'],
                    User.id != user_id
                ).first()
                if existing_user:
                    return jsonify({
                        'status': 'error',
                        'message': 'Email already exists'
                    }), 400
                user.email = data['email']
            
            if 'password' in data:
                user.password = data['password']
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'User updated successfully',
                'user': user.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    elif request.method == 'DELETE':
        """Delete user (requires password confirmation)"""
        try:
            data = request.get_json()
            
            if not data or 'password' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'Password required for deletion'
                }), 400
            
            # Verify password
            if user.password != data['password']:
                return jsonify({
                    'status': 'error',
                    'message': 'Incorrect password'
                }), 401
            
            # Delete user
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'User deleted successfully'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
