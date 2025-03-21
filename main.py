import random

class SlotMachine:
    def __init__(self, house_edge=0.05):
        self.house_edge = house_edge

    def spin(self, bet_amount):
        # Basic 3-reel slot machine
        reels = ['🍒', '🍋', '🍊', '🍉', '🍇']
        result = [random.choice(reels) for _ in range(3)]
        
        # Calculate winnings based on result
        if result[0] == result[1] == result[2]:
            win_amount = bet_amount * 10  # Win multiplier (for simplicity)
        else:
            win_amount = 0

        # Subtract house edge
        net_win = win_amount * (1 - self.house_edge)
        
        return result, net_win


# Example of a spin
slot_machine = SlotMachine()
bet = 1  # Player bets 1 Bitcoin
result, payout = slot_machine.spin(bet)

print(f"Spin result: {result}")
print(f"Payout (after house edge): {payout} BTC")
