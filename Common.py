

from enum import Enum

class Ministry(Enum):
    Peace = 1
    Plenty = 2
    Truth = 3
    Love = 4

class Classes(Enum):
   Proles = 1
   OuterParty = 2
   InnerParty = 3

class CauseOfDeath(Enum):
   Hunger = 1
   BombAttack = 2
   Execution = 3 # The agent died from ministry of love execution
   Murder = 4 # The agent died from murder by rebelled agents

class RebelOuterPartyActions(Enum):
   KillProle = 1
   KillOuterParty = 2
   Misfunction = 3

class RebelProleActions(Enum):
   KillProle = 1
   KillOuterParty = 2
   Misfunction = 3

