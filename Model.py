### Mesa version = 3.0.3
import mesa
import random

from enum import Enum

from BombAttack import BombAttack
from InnerParty import InnerParty
from LoveMinistry import LoveMinistry
from OuterParty import OuterParty
from PeaceMinistry import PeaceMinistry
from PlentyMinistry import PlentyMinistry
from Proles import Proles
from TruthMinistry import TruthMinistry


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
      initialFoodStock = 3, # the initial food that every agent has
      minFoodCRate = 1,
      maxFoodCRate = 3,
      minFoodPRate = 2,
      maxFoodPRate = 4,
      minWeaponPRate = 1,
      maxWeaponPRate = 3,
  ):
    super().__init__()
    
    # Initialize a random number generator
    self.random = random.Random()

    self.initial_population = initial_population
    self.agentDistribution = agentDistribution
    self.numberOfInnerParty = 0
    self.ministryResourcesDistribution = ministryResourcesDistribution
    
    self.minFoodCRate = minFoodCRate
    self.maxFoodCRate = maxFoodCRate
    self.minFoodPRate = minFoodPRate
    self.maxFoodPRate = maxFoodPRate
    self.minWeaponPRate = minWeaponPRate
    self.maxWeaponPRate = maxWeaponPRate

    self.initialFoodStock = initialFoodStock

    # Initiate width and height og the sugar space
    self.width = width
    self.height = height
    # The position that already has an agent on it
    self.spotTaken = []
    # The agents that died in current step
    self.diedAgent = {}
    for cause in CauseOfDeath:
       self.diedAgent[cause.name] = []

    # The rebelled agents
    self.rebeledAgents = {
       Classes.OuterParty:[],
       Classes.Proles:[]
    }


    # four ministry members
    self.ministryMembers = {
        Ministry.Love: {
            Classes.OuterParty: [],
        },
        Ministry.Truth: {
            Classes.OuterParty: [],
        },
        Ministry.Plenty: {
            Classes.OuterParty: [],
            Classes.Proles: [],
        },
        Ministry.Peace: {
            Classes.OuterParty: [],
            Classes.Proles: [],
        }
    }

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

    self.initial_population = initial_population

    # Initialize agents
    self.initializeInnerParty()
    self.initalizeOuterParty()
    self.initializeProles()

    # Initialize four minitries
    self.peaceMinistry = PeaceMinistry(
       proles = self.ministryMembers[Ministry.Peace][Classes.Proles],
       outerParties = self.ministryMembers[Ministry.Peace][Classes.OuterParty],
       nInnerParty = self.numberOfInnerParty
    )

    self.plentyMinistry = PlentyMinistry(
       proles = self.ministryMembers[Ministry.Plenty][Classes.Proles],
       outerParties = self.ministryMembers[Ministry.Plenty][Classes.OuterParty],
       nInnerParty = self.numberOfInnerParty
    )

    self.loveMinistry = LoveMinistry(
       outerParties = self.ministryMembers[Ministry.Love][Classes.OuterParty],
       nInnerParty = self.numberOfInnerParty
    )

    self.truthMinistry = TruthMinistry(
       outerParties = self.ministryMembers[Ministry.Truth][Classes.OuterParty],
       nInnerParty = self.numberOfInnerParty
    )

    # Initialize bomb attack
    self.bomb = BombAttack(
       frequency = bombAttackFrequency, 
       maxImpactSize = maxBombAttackImpactSize,
       width = self.width,
       height = self.height
    )

    pass


  """
  Proles should do their production
  OuterParty should fulfill their duty
  InnerParty should fulfill their duty
  Bomb should prepare to attack randomly
  """
  def step(self):
    # Get rebelled agent activity
    self.getRebelledAgentActivity()

    # Food production, the proles produces food, then get distruibuted
    self.plentyMinistry.generateAndDistributeFood()

    # Weapon production

    # Bomb attack

    # Food consumption

    # Other logic such as rebel and etc.


  def getRebelledAgentActivity(self):
     """
      Since the rebelled agent can do a varity of actions, and we decide to let the rebelled
      agent randomly choose one action at a time, since all the action also have possibilities
     """
     self.rebeledAgents = {
       Classes.OuterParty:[],
       Classes.Proles:[]
    }


  def initializeInnerParty(self):
    # Initialize InnerParty
    self.numberOfInnerParty = self.agentDistribution[Classes.InnerParty]*self.initial_population
    for i in range(self.numberOfInnerParty):
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
            foodCRate=self.getFoodConsumeRate(self.minFoodCRate,self.maxFoodCRate),  # The unit of food get consumed
            foodStock=self.initialFoodStock,
        )
        self.grid.place_agent(innerParty, (x, y))
        self.schedule.add(innerParty)

        # Mark the spot as taken
        self.spotTaken.append((x, y))
  

  def initalizeOuterParty(self):
    # Initialize OuterParty
    numberOfOuterParty = self.agentDistribution[Classes.OuterParty]*self.initial_population
    outerPartyMinistryDistribution = get_ministry_distribution(self.ministryResourcesDistribution, Classes.OuterParty)
    
    for i in range(numberOfOuterParty):
        # Find a unique spot for the OuterParty agent
        while True:
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            if (x, y) not in self.spotTaken:  # Ensure the spot is not already taken
                break  # Exit the loop when an empty spot is found

        
        # get the ministry for outer party
        ministry = get_Ministry_for_outer_party_and_prole(i, outerPartyMinistryDistribution)

        # Create and place the OuterParty agent
        outerParty = OuterParty(
            model=self,
            pos=(x, y),
            loyalty = 100, # The agent should start with full loyalty score
            alive=True,
            foodCRate=self.getFoodConsumeRate(self.minFoodCRate,self.maxFoodCRate),  # The unit of food get consumed
            foodStock=self.initialFoodStock,
            senseOfHunger = 0, # The agent should start with 0 sense of hunger
            senseOfSafety = 0, # The agent should start with 0 sense of safetly
            rebel = False,
            ministry = ministry
        )
        # put the outer party into certain ministry
        self.ministryMembers[ministry][Classes.OuterParty].append(outerParty)
            
        self.grid.place_agent(outerParty, (x, y))
        self.schedule.add(outerParty)

        # Mark the spot as taken
        self.spotTaken.append((x, y))

  def initializeProles(self):
    # Initialize Proles
    numberOfProles = self.agentDistribution[Classes.Proles]*self.initial_population
    prolesMinistryDistribution = get_ministry_distribution(self.ministryResourcesDistribution, Classes.Proles)

    for i in range(numberOfProles):
        # Find a unique spot for the Prole agent
        while True:
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            if (x, y) not in self.spotTaken:  # Ensure the spot is not already taken
                break  # Exit the loop when an empty spot is found

        ministry = get_Ministry_for_outer_party_and_prole(i, prolesMinistryDistribution)
       
        # Create and place the Prole agent
        prole = Proles(
            model=self,
            pos=(x, y),
            loyalty = 100, # The agent should start with full loyalty score
            alive= True,
            foodCRate= self.getFoodConsumeRate(self.minFoodCRate,self.maxFoodCRate),  # The unit of food get consumed
            foodPRate = self.getFoodProductionRate(self.minFoodPRate,self.maxFoodPRate), 
            foodStock= self.initialFoodStock,
            senseOfHunger = 0, # The agent should start with 0 sense of hunger
            senseOfSafety = 0, # The agent should start with 0 sense of safetly
            weaponPRate = self.getWeaponProductionRate(self.minWeaponPRate, self.maxWeaponPRate),
            rebel = False,
            ministry = ministry,
        )

        # put the proles into certain ministry
        self.ministryMembers[ministry][Classes.Proles].append(prole)

  def getFoodConsumeRate(self, minConsumption, maxConsumption):
    """
    Return a normal distruibution sampled food consumption rate
    """
    return self.random.uniform(minConsumption, maxConsumption+1)

  def getFoodProductionRate(self, minProduction, maxProduction):
    """
    Return a normal distruibution sampled food production rate
    """
    return self.random.uniform(minProduction, maxProduction+1)

  def getWeaponProductionRate(self, minProduction, maxProduction):
    """
    Return a normal distruibution sampled weapon production rate
    """
    return self.random.uniform(minProduction, maxProduction+1)

def get_ministry_distribution(ministryResourcesDistribution, class_type):
    """
    Calculate the range of indices for the specified class type across ministries.

    Args:
        ministryResourcesDistribution (dict): A dictionary mapping ministries to resource allocations.
        class_type (Enum): The class type to calculate the range for (e.g., Classes.OuterParty, Classes.Proles).

    Returns:
        dict: A dictionary mapping ministries to index ranges for the specified class type.
    """
    distribution_range = {}
    current_index = 1  # Start indexing from 1

    for ministry, allocation in ministryResourcesDistribution.items():
        if class_type in allocation:
            count = allocation[class_type]
            # Store the range of indices for this ministry
            distribution_range[ministry] = (current_index, current_index + count - 1)
            current_index += count

    return distribution_range


# Function to determine the ministry for a given index
def get_Ministry_for_outer_party_and_prole(index, ministryRange):
    for ministry, (start, end) in ministryRange.items():
        if start <= index <= end:
            return ministry
    return None  # In case the index is out of range



