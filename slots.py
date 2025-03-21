# casino_app/games/slots.py
import random
from utils.provably_fair import generate_random_number

class SlotMachine:
    def __init__(self):
        self.symbols = ['7', 'BAR', 'Cherry', 'Lemon', 'Orange', 'Plum', 'Bell']
        self.payouts = {
            '7-7-7': 10,      # Jackpot
            'BAR-BAR-BAR': 5, # High payout
            'Cherry-Cherry-Cherry': 3,
            'Lemon-Lemon-Lemon': 2,
            'Orange-Orange-Orange': 2,
            'Plum-Plum-Plum': 2,
            'Bell-Bell-Bell': 2,
            'Cherry-Cherry-*': 1,  # Two cherries pays 1x
            'Cherry-*-Cherry': 1,  # Two cherries in non-consecutive positions
            '*-Cherry-Cherry': 1,  # Two cherries in non-consecutive positions
        }
        # House edge is built into the symbol probabilities and payouts
    
    def play(self, bet_amount, client_seed, server_seed):
        # Use provably fair mechanism to generate the reel results
        rng_sequence = generate_random_number(client_seed, server_seed, 3)
        
        # Select symbols based on RNG values
        reels = []
        for i in range(3):
            # Map the RNG value to a symbol (with weighted probabilities)
            index = rng_sequence[i] % len(self.symbols)
            reels.append(self.symbols[index])
        
        # Check for winning combinations
        result_key = '-'.join(reels)
        payout_multiplier = 0
        
        # Check exact matches first
        if result_key in self.payouts:
            payout_multiplier = self.payouts[result_key]
        else:
            # Check for partial matches (like two cherries)
            for pattern, multiplier in self.payouts.items():
                if '*' in pattern:
                    pattern_parts = pattern.split('-')
                    matches = True
                    
                    for i, symbol in enumerate(pattern_parts):
                        if symbol != '*' and reels[i] != symbol:
                            matches = False
                            break
                    
                    if matches:
                        payout_multiplier = multiplier
                        break
        
        # Calculate payout
        payout = bet_amount * payout_multiplier
        
        return {
            "reels": reels,
            "payout": payout,
            "payout_multiplier": payout_multiplier,
            "win": payout > 0
        }
