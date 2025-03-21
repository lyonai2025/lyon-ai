# casino_app/auth/user_management.py
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from db.database import get_db

# Initialize JWT and blueprint
jwt = JWTManager()
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    db = get_db()
    
    # Check if user exists
    if db.users.find_one({"username": data['username']}):
        return jsonify({"error": "Username already exists"}), 400

    # Create new user
    hashed_password = generate_password_hash(data['password'])
    new_user = {
        "username": data['username'],
        "password": hashed_password,
        "email": data['email'],
        "balance": 0,
        "vip_status": "standard",
        "created_at": db.server_timestamp()
    }
    
    user_id = db.users.insert_one(new_user).inserted_id
    
    # Create initial wallet for the user
    db.wallets.insert_one({
        "user_id": user_id,
        "bitcoin_address": "",  # To be generated or provided by user
        "balance": 0,
        "transactions": []
    })
    
    return jsonify({"message": "User registered successfully"}), 201

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()
    
    user = db.users.find_one({"username": data['username']})
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=str(user['_id']))
    return jsonify({"token": access_token, "user_id": str(user['_id'])}), 200

@auth_blueprint.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    db = get_db()
    
    user = db.users.find_one({"_id": current_user_id})
    wallet = db.wallets.find_one({"user_id": current_user_id})
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Remove sensitive information
    user.pop('password', None)
    
    return jsonify({
        "user": user,
        "wallet": wallet
    }), 200
