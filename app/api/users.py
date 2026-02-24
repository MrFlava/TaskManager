from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.models import db, User
from app.api.schemas import (
    UserCreateIn,
    UserCreatedOut,
    UserDeleteIn,
    UserDeletedOut,
    UserOut,
    UserSingleOut,
    UsersListOut,
    UserUpdateIn,
    UserUpdatedOut,
    validation_error_payload,
)

# Create Blueprint for user routes
users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET', 'POST'])
def users():
    """List all users or create a new user"""
    if request.method == 'GET':
        """List all users"""
        try:
            users = User.query.all()
            payload = UsersListOut(
                count=len(users),
                users=[UserOut(**user.to_dict()) for user in users],
            ).model_dump()
            return jsonify(payload)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    elif request.method == 'POST':
        """Create a new user"""
        try:
            data = request.get_json(silent=True) or {}
            try:
                payload_in = UserCreateIn.model_validate(data)
            except ValidationError as ve:
                return jsonify(validation_error_payload(ve)), 422
            
            # Check for duplicate email
            existing_user = User.query.filter_by(email=str(payload_in.email)).first()
            if existing_user:
                return jsonify({
                    'status': 'error',
                    'message': 'Email already exists'
                }), 400
            
            # Create new user
            user = User(
                name=payload_in.name,
                email=str(payload_in.email),
                password=payload_in.password
            )
            
            db.session.add(user)
            db.session.commit()
            
            payload = UserCreatedOut(user=UserOut(**user.to_dict())).model_dump()
            return jsonify(payload), 201
            
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
            payload = UserSingleOut(user=UserOut(**user.to_dict())).model_dump()
            return jsonify(payload)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    elif request.method == 'PATCH':
        """Update user (partial update allowed)"""
        try:
            data = request.get_json(silent=True) or {}
            try:
                payload_in = UserUpdateIn.model_validate(data)
            except ValidationError as ve:
                return jsonify(validation_error_payload(ve)), 422
            if payload_in.model_dump(exclude_none=True) == {}:
                return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            
            # Partial update - only update provided fields
            if payload_in.name is not None:
                user.name = payload_in.name
            
            if payload_in.email is not None:
                # Check for duplicate email (excluding current user)
                existing_user = User.query.filter(
                    User.email == str(payload_in.email),
                    User.id != user_id
                ).first()
                if existing_user:
                    return jsonify({
                        'status': 'error',
                        'message': 'Email already exists'
                    }), 400
                user.email = str(payload_in.email)
            
            if payload_in.password is not None:
                user.password = payload_in.password
            
            db.session.commit()
            
            payload = UserUpdatedOut(user=UserOut(**user.to_dict())).model_dump()
            return jsonify(payload)
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    elif request.method == 'DELETE':
        """Delete user (requires password confirmation)"""
        try:
            data = request.get_json(silent=True) or {}
            try:
                payload_in = UserDeleteIn.model_validate(data)
            except ValidationError as ve:
                return jsonify(validation_error_payload(ve)), 422
            
            # Verify password
            if user.password != payload_in.password:
                return jsonify({
                    'status': 'error',
                    'message': 'Incorrect password'
                }), 401
            
            # Delete user
            db.session.delete(user)
            db.session.commit()
            
            payload = UserDeletedOut().model_dump()
            return jsonify(payload)
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
