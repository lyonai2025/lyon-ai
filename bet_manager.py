# casino_app/betting/bet_manager.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db.database import get_db

betting_blueprint = Blueprint('betting', __name__)

@betting_blueprint.route('/place-bet', methods=['POST'])
@jwt_required()
def place_bet():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    game_id = data.get('game_id')
    amount = data.get('amount')
    bet_details = data.get('bet_details', {})
    
    # Validate bet amount
    if amount <= 0:
        return jsonify({"error": "Bet amount must be positive"}), 400
    
    db = get_db()
    
    # Check user balance
    user = db.users.find_one({"_id": current_user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user['balance'] < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    # Reserve the bet amount (deduct from balance)
    db.users.update_one(
        {"_id": current_user_id},
        {"$inc": {"balance": -amount}}
    )
    
    # Create bet record
    bet_id = db.bets.insert_one({
        "user_id": current_user_id,
        "game_id": game_id,
        "amount": amount,
        "bet_details": bet_details,
        "status": "placed",
        "created_at": db.server_timestamp()
    }).inserted_id
    
    return jsonify({
        "message": "Bet placed successfully",
        "bet_id": str(bet_id),
        "remaining_balance": user['balance'] - amount
    })

@betting_blueprint.route('/bet-history', methods=['GET'])
@jwt_required()
def get_bet_history():
    current_user_id = get_jwt_identity()
    db = get_db()
    
    # Get user's betting history
    bets = list(db.bets.find({"user_id": current_user_id}).sort("created_at", -1).limit(50))
    
    # Format bets for JSON response
    formatted_bets = []
    for bet in bets:
        bet['_id'] = str(bet['_id'])
        formatted_bets.append(bet)
    
    return jsonify({"bets": formatted_bets})
