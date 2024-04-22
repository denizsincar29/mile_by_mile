# mile by mile, 1000 miles, mille bornes or however you want to call it
# This is a simple game where you have to reach 1000 miles before your opponent
# The game is played by two players, and each player has a deck of cards
# 25 miles (10x), 50 miles (10x), 75 miles (10x), 100 miles (12x), 200 miles (4x),
# start (10x), more gas, spare tire, end of limit, repair, turn around (4x each) fix cards,
# stop, out of gas, flat tire, speed limit, accident, reverse (2x each) damage cards,
# stop protect, out of gas protect, flat tire protect, speed limit protect, accident protect, reverse protect (1x each) protection cards.

# we will use the enum class from rust_enum.py, because i'm a rustacean hehe!

from rust_enum import enum, Case
#from typing import Any
from random import shuffle


# damage type enum:
@enum
class Situation:
    Stop=Case()
    Gas=Case()
    Tire=Case()
    Limit=Case()
    Accident=Case()
    Reverse=Case()

# the cards. Mile type with the value, fix, damage and protect cards with the situation value
@enum
class Card:
    Mile=Case(value=int)
    Fix=Case(situation=Situation)
    Damage=Case(situation=Situation)
    Protect=Case(situation=Situation)
    SkipTurn=Case()

    # impl card
    @property
    def card_type(self):
        match self:
            case Card.Protect(_):
                return "protect"
            case Card.Damage(_):
                return "damage"
            case Card.Fix(_):
                return "fix"
            case Card.Mile(_):
                return "mile"
            case Card.SkipTurn():
                return "skip"
            case _:
                return "unknown"  # can't happen

    def __str__(self):
        match self:
            case Card.Mile(value):
                return f"{value} miles"
            case Card.Fix(situation):
                match situation:
                    case Situation.Stop():
                        return "Start"
                    case Situation.Gas():
                        return "More gas"
                    case Situation.Tire():
                        return "Spare tire"
                    case Situation.Limit():
                        return "End of limit"
                    case Situation.Accident():
                        return "Repair"
                    case Situation.Reverse():
                        return "Turn around"
            case Card.Damage(situation):
                match situation:
                    case Situation.Stop():
                        return "Stop"
                    case Situation.Gas():
                        return "Out of gas"
                    case Situation.Tire():
                        return "Flat tire"
                    case Situation.Limit():
                        return "Speed limit"
                    case Situation.Accident():
                        return "Accident"
                    case Situation.Reverse():
                        return "Reverse"
            case Card.Protect(situation):
                match situation:
                    case Situation.Stop():
                        return "Stop protect"
                    case Situation.Gas():
                        return "Out of gas protect"
                    case Situation.Tire():
                        return "Flat tire protect"
                    case Situation.Limit():
                        return "Speed limit protect"
                    case Situation.Accident():
                        return "Accident protect"
                    case Situation.Reverse():
                        return "Reverse protect"
            case Card.SkipTurn():
                return "skip turn"
        return f"unknown card: {self.__repr__()}"  # can't happen but happens. debug it!


# deck and discard pile
class Deck:
    def __init__(self):
        self.cards = []
        for _ in range(10):
            self.cards.append(Card.Mile(25))
            self.cards.append(Card.Mile(50))
            self.cards.append(Card.Mile(75))
            # start card
            self.cards.append(Card.Fix(Situation.Stop()))
            self.cards.append(Card.SkipTurn())
        for _ in range(12):
            self.cards.append(Card.Mile(100))
        for _ in range(4):
            self.cards.append(Card.Mile(200))
            self.cards.append(Card.Fix(Situation.Gas()))
            self.cards.append(Card.Fix(Situation.Tire()))
            self.cards.append(Card.Fix(Situation.Limit()))
            self.cards.append(Card.Fix(Situation.Accident()))
            self.cards.append(Card.Fix(Situation.Reverse()))
        for _ in range(2):
            self.cards.append(Card.Damage(Situation.Stop()))
            self.cards.append(Card.Damage(Situation.Gas()))
            self.cards.append(Card.Damage(Situation.Tire()))
            self.cards.append(Card.Damage(Situation.Limit()))
            self.cards.append(Card.Damage(Situation.Accident()))
            self.cards.append(Card.Damage(Situation.Reverse()))
        self.cards.append(Card.Protect(Situation.Stop()))
        self.cards.append(Card.Protect(Situation.Gas()))
        self.cards.append(Card.Protect(Situation.Tire()))
        self.cards.append(Card.Protect(Situation.Limit()))
        self.cards.append(Card.Protect(Situation.Accident()))
        self.cards.append(Card.Protect(Situation.Reverse()))
        shuffle(self.cards)
        assert len(self.cards) == 104

        self.discard = []

    def draw(self):
        shuffled=False
        if len(self.cards) < 1:
            self.cards.extend(self.discard)
            shuffle(self.cards)
            self.discard = []
            shuffled=True
        return self.cards.pop(), shuffled # return the card and if the deck was shuffled.

    def _discard(self, card):
        self.discard.append(card)


class Player:
    def __init__(self):
        self.deck=Deck()
        self.hand = [self.deck.draw()[0] for _ in range(6)]  # [0] is the card, [1] is if the deck was shuffled. I forgot and the hand looked like [(card, shuffled), ...] haha!
        self.miles = 0
        self.reverse=1 # 0 normal, 1 reversed, 2 protected
        self.started=0 # stopped and not stop-protected
        self.speed=1 # not limited, 0 limited and 2 protected.
        self.tire=1 #0 flat, 1 normal, 2 protected
        self.gas=1
        self.accident=1

    @property
    def direction(self):
        # 1 normal, -1 reversed, for multiplying miles.
        if self.reverse==0:
            return -1
        return 1

    def go(self, miles: int, check=False):
        # if check, return if can go. if not check, go and return if can go.
        if self.started==0 or (self.started==2 and self.tire==0 and self.gas==0 and self.accident==0):
            return False
        if miles>50 and self.speed==0:
            return False
        if not (0<=self.miles+miles*self.direction<1000):  # if not in range, can't go.
            return False
        if not check:
            self.miles += miles*self.direction
        return True

    def state(self, situation: Situation):
        match situation:
            case Situation.Stop():
                return self.started
            case Situation.Gas():
                return self.gas
            case Situation.Tire():
                return self.tire
            case Situation.Limit():
                return self.speed
            case Situation.Accident():
                return self.accident
            case Situation.Reverse():
                return self.reverse

    def change_state(self, situation: Situation, value: int, validate=True):
        match situation:
            case Situation.Stop():
                self.started=value
            case Situation.Gas():
                self.gas=value
            case Situation.Tire():
                self.tire=value
            case Situation.Limit():
                self.speed=value
            case Situation.Accident():
                self.accident=value
            case Situation.Reverse():
                self.reverse=value
        if validate:
            self.validate_states()  # we changed a state, validate all states.

    def validate_states(self):
        # if flat tire, out of gas or accident, can't go: if not stop_protected: set started to 0.
        if (self.tire==0 or self.gas==0 or self.accident==0) and self.started==1:
            self.started=0
        

    def damage(self, situation, check=False):
        # if check, return if can damage. if not check, damage and return if damaged.
        if self.state(situation)!=1: # if protected or already damaged,
            return False # can't damage
        if not check: # damage!
            self.change_state(situation, 0)
        return True # damaged or can damage!

    def protect(self, situation, check=False):
        # if check, return if can protect. if not check, protect and return if protected.
        if self.state(situation)==2:
            return False  # already protected
        if not check:
            self.change_state(situation, 2)
        return True

    def fix(self, situation, check=False):
        # if check, return if can fix. if not check, fix and return if fixed.
        if self.state(situation)>0: # if not damaged or protected, can't fix.
            return False
        if not check: # fix!
            self.change_state(situation, 1)
        return True # fixed or can fix!


    def play(self, card, on_another_player=None, check=False):
        # remove card from hand and play it.
        if not check:
            self.hand.remove(card)
        match card:
            case Card.Mile(value):
                return self.go(value, check)
            case Card.Fix(situation):
                return self.fix(situation, check)
            case Card.Damage(situation):
                # we can't damage ourselves, so we damage the other player haha!
                if on_another_player is None:
                    return ... # card is playable but another player is needed.
                return on_another_player.damage(situation, check)
            case Card.Protect(situation):
                return self.protect(situation, check)
            case Card.SkipTurn():
                return True # the next player will be the current player, so nothing to do.
            case val:
                raise ValueError(f"something went horribly wrong! The case fell to {val}")
    


    def draw(self):
        self.hand.append(self.deck.draw()[0])
        return self.hand[-1]

    def discard(self, card):
        self.deck._discard(card)
        self.hand.remove(card)

    def __str__(self):
        return f"Player(miles={self.miles}, hand={self.hand})"    

class Game:
    def __init__(self, players=2, miles=1000):
        self.players = [Player() for _ in range(players)]
        self.current_player = 0
        self.winner = None

    def draw(self):
        drew=None
        while len(self.players[self.current_player].hand)<7:
            drew=self.players[self.current_player].draw()
        return drew
    def discard(self, card):
        self.players[self.current_player].discard(card)

    def discard_idx(self, idx):
        print(idx, "of", len(self.players))
        self.players[self.current_player].discard(self.players[self.current_player].hand[idx])
        self.next_player()

    def whom_can_damage(self, card):
        return [i for i, player in enumerate(self.players) if player!=self.players[self.current_player] and self.players[self.current_player].play(card, player, check=True)]  # oh, so long!
    
    def can_damage(self, card):
        # if the card can damage any player, return True.
        return len(self.whom_can_damage(card))>0

    def get_hand(self):
        # [(card, playable), ...]
        #print(self.players[self.current_player].hand)
        return [(card, self.players[self.current_player].play(card, check=True)) for card in self.players[self.current_player].hand]


    def play(self, card, on_another_player=None, check=False):
        played=self.players[self.current_player].play(card, on_another_player, check)
        # if not a protect card, next player!
        if not check and played and (card.card_type!="protect" or card.card_type!="skip"):  # if skip, the same player will play again.
            self.next_player()
        if played==... and not self.can_damage(card):
            return False
        return played

    def next_player(self):
        self.current_player = (self.current_player+1)%len(self.players)
        return self.current_player

    def check_winner(self):
        if self.players[self.current_player].miles>=1000:
            self.winner = self.current_player
            return True
        return False

    def search_for_card_by_name(self, name):
        for i, card in enumerate(self.players[self.current_player].hand):
            if name in str(card):
                return i
        return None

    def get_hand_str(self):
        print(self.get_hand())
        return "\n".join([str(card)+ (" is playable" if playable else "") for card, playable in self.get_hand()])

    def __str__(self):
        return f"Game(players={self.players}, winner={self.winner})"


# helper function for interactive game.
def intinput(prompt, min, max):
    while True:
        try:
            i=int(input(prompt))
            if min<=i<=max:
                return i
            print(f"Please enter a number between {min} and {max}!")
        except ValueError:
            print("Please enter a valid number!")


if __name__ == "__main__":
    print("Mile by mile, 1000 miles, mille bornes or however you want to call it!")
    print("tip: play a card by typing it's name, put an exclamation mark at the end to discard it.")
    print("Lets begin the game!")
    game = Game()

    while not game.check_winner():
        current=game.current_player
        print(f"Player {current}'s turn!")
        drew=game.draw()
        if drew:
            print(f"new card {drew}")
        print(f"Your cards:\n{game.get_hand_str()}")
        card_name = input("Play a card: ")
        idx=game.search_for_card_by_name(card_name.strip().removeprefix("!"))
        if idx is None:
            print("Card not found!")
            continue
        real_card_name = game.get_hand()[idx][0]
        if card_name.endswith("!"):
            print(f"You threw away the {real_card_name} card!")
            game.discard_idx(idx)
        else:
            card= game.get_hand()[idx][0]
            played=game.play(card)
            if not played:
                print(f"Can't play {real_card_name} card! would you like to discard it? (y/n)")
                if input().strip().lower()=="y":
                    game.discard_idx(idx)
                    print(f"You threw away the {real_card_name} card!")
                else:
                    print("ok, let's try again!")
            elif played==...:
                opponent=-1
                if len(game.players)==2:
                    opponent=(current+1)%2
                else:
                    print(f"You played the {real_card_name} card! Who would you like to damage? (type the number of your opponent.)")
                    opponent=intinput("Opponent number: ", 0, len(game.players)-1)
                    if opponent==current:
                        print("You can't damage yourself!")
                        continue
                played=game.play(card, game.players[opponent])
                if played:
                    print(f"You played the {real_card_name} card on player {opponent}!")
                else:
                    print("this player is protected" if game.players[opponent].state(card.situation)==2 else "this player is already damaged")
        if game.check_winner():
            print(f"Player {current} won the game!")
    print("Game over!")
    print(game)               