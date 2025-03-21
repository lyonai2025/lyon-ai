# casino_app/main.py
import os
import logging
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Import app components
from auth.user_management import auth_blueprint, jwt
from games.game_manager import game_blueprint
from betting.bet_manager import betting_blueprint
from payments.transaction_manager import payment_blueprint
from utils.provably_fair import verify_fairness

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("casino_app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')

# Register JWT with app
jwt.init_app(app)

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
app.register_blueprint(game_blueprint, url_prefix='/api/games')
app.register_blueprint(betting_blueprint, url_prefix='/api/betting')
app.register_blueprint(payment_blueprint, url_prefix='/api/payments')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "1.0.0"})

@app.route('/api/verify-fairness', methods=['POST'])
def fairness_check():
    data = request.get_json()
    result = verify_fairness(
        data.get('game_type'),
        data.get('client_seed'),
        data.get('server_seed_hash'),
        data.get('nonce'),
        data.get('result')
    )
    return jsonify({"verified": result})

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True')
