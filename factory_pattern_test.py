"""
🎮 FACTORY PATTERN EXERCISE - VIDEO GAME CHARACTER CREATOR 🎮

SCENARIO:
You're building a video game where players can create different types of characters.
Currently, the game client has messy code with lots of conditions to create characters.

PROBLEM (Without Factory):
Every time the game needs to create a character, it has this ugly code:

if character_type == "warrior":
    char = Warrior(weapon="sword", armor="heavy", health=100, strength=80, magic=20)
elif character_type == "mage":
    char = Mage(weapon="staff", armor="robe", health=60, strength=30, magic=100)
elif character_type == "archer":
    char = Archer(weapon="bow", armor="leather", health=80, strength=60, magic=40)
elif character_type == "thief":
    char = Thief(weapon="dagger", armor="light", health=70, strength=50, magic=30)

This code appears in:
- Character creation screen
- Game save/load system
- Multiplayer lobby
- AI enemy spawner
- Character equipment shop

ISSUES:
1. Game client knows too much about character stats and equipment
2. Adding a new character class (like "paladin") requires updating 5+ files
3. If Warrior stats need rebalancing, you have to hunt down multiple places
4. New developers get confused by scattered character creation logic

YOUR TASK:
Design a Factory Pattern solution where:
1. Client just says "create a warrior"
2. Factory handles all the complex character setup
3. Adding new character types is simple
4. Stat changes happen in one place

REQUIREMENTS TO IMPLEMENT:
1. All characters should have common abilities (attack, defend, use_skill)
2. Each character type has different default stats and equipment
3. Factory should handle the creation logic
4. Client code should be clean and simple

CHARACTERS TO SUPPORT:
- Warrior: High health/strength, low magic, sword + heavy armor
- Mage: High magic, low health/strength, staff + robe
- Archer: Balanced stats, bow + leather armor  
- Thief: Fast/stealthy, dagger + light armor

BONUS CHALLENGES:
- Add character levels (level 1 warrior vs level 50 warrior)
- Add different races (elf mage vs human mage)
- Add random stat variations (+/- 10% from base stats)
- Add equipment upgrade system
- Add character skill trees

EXTENSION IDEAS:
- What if you want different difficulty modes? (easy = higher stats)
- What if different game modes need different character setups?
- How would you handle character customization (player chooses weapon)?

THINK ABOUT:
- What happens when you add "Paladin" character?
- What if Warrior base health changes from 100 to 120?
- How does a new developer learn character creation?
- What if different game levels need different enemy types?

HINT:
Think about what ALL characters can do (common interface), then think about
what makes each character type unique (specific implementations).
"""
from abc import ABC, abstractmethod

class Character(ABC):
    def __init__(self, weapon, armor, health, strength, magic):
        self.weapon = weapon
        self.armor = armor
        self.health = health
        self.strength = strength
        self.magic = magic
    
    @abstractmethod
    def create(self):
        """Abstract method to create a character."""
        return f"{self.__class__.__name__} created with {self.weapon}, {self.armor}, health: {self.health}, strength: {self.strength}, magic: {self.magic}"
    
class Warrior(Character):
    def __init__(self):
        super().__init__(
            weapon='Sword',
            armor='Heavy',
            health=100,
            strength=100,
            magic=0
        )

class Mage(Character):
    def __init__():
        super().__init__(weapon='Staff', armor='Light', health=40, strength=0, magic=100)
        

class CharacterFactory:
    def __init__(self):
        self._characters = {
            "Warrior": Warrior,
            "Mage": Mage,
        }
        
    def create_character(self, type):
        """Factory method to create characters based on class name."""
        return self._characters.get(type)()

        
user_request = "Mage"
character_factory = CharacterFactory()
new_character = character_factory.create_character(type=user_request)
        



# if character_type == "warrior":
#     char = Warrior(weapon="sword", armor="heavy", health=100, strength=80, magic=20)
# elif character_type == "mage":
#     char = Mage(weapon="staff", armor="robe", health=60, strength=30, magic=100)
# elif character_type == "archer":
#     char = Archer(weapon="bow", armor="leather", health=80, strength=60, magic=40)
# elif character_type == "thief":
#     char = Thief(weapon="dagger", armor="light", health=70, strength=50, magic=30)