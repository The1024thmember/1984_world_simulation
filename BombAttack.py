# Suppress all UserWarnings, there are some UserWarning and DeprecationWarning
# which spamming the terminal
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class BombAttack():
  """
    BombAttack:
    - Define the frequency of attack, though random, we can still adjust it
    - Define the damage size, random, can still be adjusted
    
  """
  def __init__(self, 
               frequency, # how frequently the attack will happen
               maxImpactSize, # the maximum impact area size
               width, # the width of the map
               height, # the height of the map
               ):
    self.frequency = frequency
    self.maxImpactSize = maxImpactSize
    self.historicalAttacks = [] # record the historical attacks

  def attack(self):
    """
      Generate the scope and position of attack randomly, according to the frequency
      return the position of the bomb attack
    """
    pass
