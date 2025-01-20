### Mesa version = 3.0.3
import mesa
import random

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

class BasicModel(mesa.Model):
  """
  BasicModel simulates the society described in 1984.
  External environment: at war, there will be random bomb attack on random location with random impact from time to time,
  the agent will be killed the agent is placed in the bomb's impact area.

  Internal environment: there are three types of agents, InnerParty, OuterParty, and Proles
  They will be initialized based on certain percentage, and initialized at random location.


  In this model, the population will be a dynamic value, since there are few ways that agent can die from this model,
  (check for maybe_die() function in each agent model for detail) and the goal is to see how long the society will last.
  """
  def __init__(
      self,
      bombAttackFrequency, # bomb attack frequency
      maxBombAttackImpactSize, # maximum bomb attack impact on its size
      agentDistribution = {  # the different agent population distruibution
        Classes.Proles: 0.85,
        Classes.OuterParty: 0.13,
        Classes.InnerParty: 0.02
      },
      ministryResourcesDistribution = { # the initial distribution of resources among ministries
         Ministry.Love: {
            Classes.OuterParty: 3,
         },
         Ministry.Peace: {
            Classes.OuterParty: 8,
            Classes.Proles: 85,
         },
         Ministry.Truth: {
            Classes.OuterParty: 7,
         },
         Ministry.Plenty: {
            Classes.OuterParty: 8,
            Classes.Proles: 85,
         }
      },
      width = 17, # we want to ensure population will not fill the space, since the outerparty can move around 
      height = 17, 
      initial_population = 200, # initial population
  ):
    super().__init__()

    self.initial_population = initial_population
    self.agentDistribution = agentDistribution
    self.ministryResourcesDistribution = ministryResourcesDistribution
    # Initiate width and height og the sugar space
    self.width = width
    self.height = height
    # The position that already has an agent on it
    self.spotTaken = []

    # Initiate mesa grid class
    self.grid = mesa.space.MultiGrid(
        width = self.width, 
        height = self.height, 
        torus = True
      )

    # initiate data collector
    self.datacollector = mesa.DataCollector(
      model_reporters = {},
      agent_reporters = {}
    )

    # Scheduler
    self.schedule = mesa.time.RandomActivationByType(self)

    # Initialize a random number generator
    self.random = random.Random()
    self.initial_population = initial_population

    # Initialize InnerParty
    numberOfInnerParty = agentDistribution[Classes.InnerParty]*self.initial_population
    for i in range(numberOfInnerParty):
        # Find a unique spot for the InnerParty agent
        while True:
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            if (x, y) not in self.spotTaken:  # Ensure the spot is not already taken
                break  # Exit the loop when an empty spot is found

        # Create and place the InnerParty agent
        innerParty = InnerParty(
            model=self,
            pos=(x, y),
            alive=True,
            foodCRate=1.0,  # The unit of food get consumed
            foodStock=0,
        )
        self.grid.place_agent(innerParty, (x, y))
        self.schedule.add(innerParty)

        # Mark the spot as taken
        self.spotTaken.append((x, y))

    # Initialize OuterParty
    numberOfOuterParty = agentDistribution[Classes.OuterParty]*self.initial_population
    outerPartyMinistryDistribution = getOuterPartyMinistryDistruibution(self.ministryResourcesDistribution)
    
    for i in range(numberOfOuterParty):
        # Find a unique spot for the InnerParty agent
        while True:
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            if (x, y) not in self.spotTaken:  # Ensure the spot is not already taken
                break  # Exit the loop when an empty spot is found

        
        # Create and place the InnerParty agent
        innerParty = OuterParty(
            model=self,
            pos=(x, y),
            loyalty = 100, # The agent should start with full loyalty score
            alive=True,
            foodCRate=1.0,  # The unit of food get consumed
            foodStock=0,
            senseOfHunger = 0, # The agent should start with 0 sense of hunger
            senseOfSafety = 0, # The agent should start with 0 sense of safetly
            rebel = False,
            ministry =  getMinistryForOuterParty(i, outerPartyMinistryDistribution)
        )
        self.grid.place_agent(innerParty, (x, y))
        self.schedule.add(innerParty)

        # Mark the spot as taken
        self.spotTaken.append((x, y))


    # Initialize Proles

    # Initialize bomb attack
    bomb = BombAttack(
       frequency = bombAttackFrequency, 
       maxImpactSize = maxBombAttackImpactSize,
       width = self.width,
       height = self.height
    )


  """
  Proles should do their production
  OuterParty should fulfill their duty
  InnerParty should fulfill their duty
  Bomb should prepare to attack randomly
  """
  def step(self):
    pass


# To map the range of indices to the corresponding ministry
def getOuterPartyMinistryDistruibution(ministryResourcesDistribution):
  outerPartyRange = {}
  current_index = 1  # Start indexing from 1
  for ministry, allocation in ministryResourcesDistribution.items():
      if Classes.OuterParty in allocation:
          count = allocation[Classes.OuterParty]
          # Store the range of indices for this ministry
          outerPartyRange[ministry] = (current_index, current_index + count - 1)
          current_index += count
  return outerPartyRange

# Function to determine the ministry for a given index
def getMinistryForOuterParty(index, outerPartyRange):
    for ministry, (start, end) in outerPartyRange.items():
        if start <= index <= end:
            return ministry
    return None  # In case the index is out of range
