# casino_app/games/game_manager.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db.database import get_db
from games.slots import SlotMachine
from games.blackjack import BlackjackGame
from games.roulette import RouletteGame
from games.poker import PokerGame
from utils.provably_fair import generate_server_seed, hash_server_seed

game_blueprint = Blueprint('games', __name__)

# Game factory to create the right game instance
def get_game_instance(game_type):
    game_classes = {
        'slots': SlotMachine,
        'blackjack': BlackjackGame,
        'roulette': RouletteGame,
        'poker': PokerGame
    }
    
    game_class = game_classes.get(game_type)
    if not game_class:
        return None
    
    return game_class()

@game_blueprint.route('/available', methods=['GET'])
def get_available_games():
    games = [
        {"id": "slots", "name": "Slot Machine", "min_bet": 1, "max_bet": 100},
        {"id": "blackjack", "name": "Blackjack", "min_bet": 5, "max_bet": 500},
        {"id": "roulette", "name": "Roulette", "min_bet": 1, "max_bet": 1000},
        {"id": "poker", "name": "Poker", "min_bet": 10, "max_bet": 1000}
    ]
    return jsonify({"games": games})

@game_blueprint.route('/prepare', methods=['POST'])
@jwt_required()
def prepare_game():
    data = request.get_json()
    game_type = data.get('game_type')
    
    # Generate server seed for provably fair gameplay
    server_seed = generate_server_seed()
    server_seed_hash = hash_server_seed(server_seed)
    
    # Store seed for later verification
    db = get_db()
    db.game_seeds.insert_one({
        "user_id": get_jwt_identity(),
        "game_type": game_type,
        "server_seed": server_seed,
        "server_seed_hash": server_seed_hash,
        "used": False,
        "created_at": db.server_timestamp()
    })
    
    return jsonify({
        "game_type": game_type,
        "server_seed_hash": server_seed_hash,
        "message": "Game prepared, ready for client seed"
    })

@game_blueprint.route('/play', methods=['POST'])
@jwt_required()
def play_game():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    game_type = data.get('game_type')
    bet_amount = data.get('bet_amount')
    client_seed = data.get('client_seed')
    server_seed_hash = data.get('server_seed_hash')
    
    # Get game instance
    game = get_game_instance(game_type)
    if not game:
        return jsonify({"error": "Invalid game type"}), 400
    
    # Get the server seed
    db = get_db()
    seed_doc = db.game_seeds.find_one({
        "user_id": current_user_id,
        "server_seed_hash": server_seed_hash,
        "used": False
    })
    
    if not seed_doc:
        return jsonify({"error": "Invalid or used server seed"}), 400
    
    # Check if user has enough balance
    user = db.users.find_one({"_id": current_user_id})
    if user['balance'] < bet_amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    # Play the game with the seeds
    result = game.play(
        bet_amount=bet_amount,
        client_seed=client_seed,
        server_seed=seed_doc['server_seed']
    )
    
    # Mark the seed as used
    db.game_seeds.update_one(
        {"_id": seed_doc['_id']},
        {"$set": {"used": True}}
    )
    
    # Record game result
    db.game_results.insert_one({
        "user_id": current_user_id,
        "game_type": game_type,
        "bet_amount": bet_amount,
        "result": result,
        "client_seed": client_seed,
        "server_seed": seed_doc['server_seed'],
        "server_seed_hash": server_seed_hash,
        "timestamp": db.server_timestamp()
    })
    
    # Update user balance
    new_balance = user['balance'] + result['payout'] - bet_amount
    db.users.update_one(
        {"_id": current_user_id},
        {"$set": {"balance": new_balance}}
    )
    
    return jsonify({
        "result": result,
        "new_balance": new_balance,
        "server_seed": seed_doc['server_seed']  # Reveal the server seed after use
    })
