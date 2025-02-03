# Suppress all UserWarnings, there are some UserWarning and DeprecationWarning
# which spamming the terminal
import random


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
               avgImpactSize, # the average impact area size
               avgIntensity, # the average intensity for the bomb attack
               width, # the width of the map
               height, # the height of the map
               ):
    self.frequency = frequency
    self.avgImpactSize = avgImpactSize
    self.avgIntensity = avgIntensity
    # record the historical attacks
    # eg: [[center_x, center_y, radius, intensity], ...]
    self.historicalAttacks = [] 

  def attack(self):
      """
      Generate the scope and position of attack randomly, according to the frequency.
      The larger the impact size, the less frequent the attacks.
      The size is determined based on historical attacks.
      Returns:
          List of coordinates affected by the bomb impact.
      """
      # Randomly select a center point
      center_x = random.randint(0, self.width - 1)
      center_y = random.randint(0, self.height - 1)

      # Determine impact radius based on historical attacks
      if self.historicalAttacks:
          avg_past_radius = sum(r for _, _, r, i in self.historicalAttacks) / len(self.historicalAttacks)
          radius = min(self.avgImpactSize, max(1, int(avg_past_radius * random.uniform(0.5, 1.5))))
          intensity = min(self.avgIntensity, max(1, int(avg_past_radius * random.uniform(0.5, 1.5))))
      else:
          radius = random.randint(1, self.avgImpactSize)
          intensity = random.randint(1, self.avgIntensity)

      # Generate affected coordinates within bounds
      affected_area = []
      for dx in range(-radius, radius + 1):
          for dy in range(-radius, radius + 1):
              if dx ** 2 + dy ** 2 <= radius ** 2:  # Ensure it's within the circle
                  new_x = center_x + dx
                  new_y = center_y + dy
                  if 0 <= new_x < self.width and 0 <= new_y < self.height:
                      affected_area.append((new_x, new_y))

      # Record attack
      self.historicalAttacks.append((center_x, center_y, radius, intensity))

      return affected_area
