# casino_app/utils/provably_fair.py
import hashlib
import hmac
import secrets
import random

def generate_server_seed(length=32):
    """Generate a random server seed."""
    return secrets.token_hex(length)

def hash_server_seed(server_seed):
    """Hash the server seed to share with client while keeping the original secret."""
    return hashlib.sha256(server_seed.encode()).hexdigest()

def generate_random_number(client_seed, server_seed, num_results=1, min_val=0, max_val=1000000):
    """
    Generate provably fair random numbers using client and server seeds.
    
    Args:
        client_seed: Seed provided by the client
        server_seed: Private seed generated by the server
        num_results: Number of random numbers to generate
        min_val: Minimum value (inclusive)
        max_val: Maximum value (exclusive)
        
    Returns:
        List of random numbers
    """
    if not client_seed or not server_seed:
        raise ValueError("Both client_seed and server_seed must be provided")
    
    # Create a message using client seed and initial nonce
    message = f"{client_seed}".encode()
    
    # Use HMAC with SHA-256 for generating random bytes
    h = hmac.new(server_seed.encode(), message, hashlib.sha256).digest()
    
    results = []
    for i in range(num_results):
        if i > 0:
            # If we need more than one number, update the message with previous hash
            message = h
            h = hmac.new(server_seed.encode(), message, hashlib.sha256).digest()
            
        # Convert hash bytes to integer and scale to desired range
        value = int.from_bytes(h, byteorder='big')
        scaled_value = min_val + (value % (max_val - min_val))
        results.append(scaled_value)
    
    return results

def verify_fairness(game_type, client_seed, server_seed_hash, server_seed, nonce, game_result):
    """
    Verify that a game result is fair by checking if it matches what would be
    produced using the provided seeds.
    
    Args:
        game_type: Type of game (slots, roulette, etc.)
        client_seed: Seed provided by the client
        server_seed_hash: Hash of the server seed that was shown before the game
        server_seed: The revealed server seed after the game
        nonce: The nonce used in the game
        game_result: The result to verify
        
    Returns:
        bool: True if the result is verified, False otherwise
    """
    # Verify the server_seed matches its hash
    calculated_hash = hash_server_seed(server_seed)
    if calculated_hash != server_seed_hash:
        return False
    
    # This verification would differ based on game type
    # Here's a simple verification for slots as an example
    if game_type == 'slots':
        from games.slots import SlotMachine
        slot_machine = SlotMachine()
        expected_result = slot_machine.play(0, client_seed, server_seed)  # Bet amount doesn't affect the reels
        return expected_result['reels'] == game_result['reels']
    
    # Implementation for other game types would go here
    
    return False
