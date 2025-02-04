### Mesa version = 3.0.3
import mesa
import random


from BombAttack import BombAttack
from Common import CauseOfDeath, Classes, Ministry, RebelOuterPartyActions, RebelProleActions
from InnerParty import InnerParty
from LoveMinistry import LoveMinistry
from OuterParty import OuterParty
from PeaceMinistry import PeaceMinistry
from PlentyMinistry import PlentyMinistry
from Proles import Proles
from TruthMinistry import TruthMinistry

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
      avgBombAttackImpactSize, # average bomb attack impact on its size
      avgBombAttackIntensity, # average bomb attack intensity
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
    # Assign probabilities to each action
    self.outer_party_probabilities = {
        RebelOuterPartyActions.KillProle: 0.1,       # 10% chance
        RebelOuterPartyActions.KillOuterParty: 0.2,  # 20% chance
        RebelOuterPartyActions.Misfunction: 0.7      # 70% chance
    }

    self.prole_probabilities = {
        RebelProleActions.KillProle: 0.4,            # 40% chance
        RebelProleActions.KillOuterParty: 0.1,       # 10% chance
        RebelProleActions.Misfunction: 0.5          # 50% chance
    }
    
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
    # eg: [[agent, (x,y)], [agent, (x,y)]] 
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
       avgImpactSize = avgBombAttackImpactSize,
       avgIntensity = avgBombAttackIntensity,
       width = self.width,
       height = self.height)

    pass


  def step(self):
    """
    Proles should do their production
    OuterParty should fulfill their duty
    InnerParty should fulfill their duty
    Bomb should prepare to attack randomly

    Be aware that all the death happened in this round will only take effect in the next round, 
    as the InnerParty allocate resources based on percentage of member in self.ministryMembers
    at the end of each step and self.ministryMembers updates the number of died agent during
    the step process
    """
    
    # Get rebelled agent activity
    self.getRebelledAgentActivity()

    # Food production, the proles produces food, then get distruibuted
    self.plentyMinistry.generateAndDistributeFood(self.spotTaken, gridSize = self.height)

    # Weapon production
    self.peaceMinistry.collectWeapons()

    # Bomb attack, it is a rare event
    # 1. Defend bomb attack
    # 2. Calculate Casualty
    # 3. Spread of sense of safety via network effect
    if random.randint(0,10)<2:
      # step 1: defend bomb attack
      attackedLocation = self.peaceMinistry.defendBombAttack(self.bomb)
      for pos in attackedLocation:
        this_cell = self.grid.get_cell_list_contents(pos)
        for agent in this_cell:
          # need to ensure the agent is removed from the ministry as well
          if isinstance(agent, Proles) or isinstance(agent, OuterParty) or isinstance(agent, InnerParty):
            # step 2: calculate casualty
            agent.die()
            self.removeAgentFromSpot(agent)
            self.removeAgentFromMinistry(agent)
            self.diedAgent[CauseOfDeath.BombAttack].append(agent)
            # step 3: spread sense of safety
            self.spreadSenseOfSatefy(agent)

    # Food consumption
    # 1. Consume food
    # 2. Calculate Casualty
    # 3. Spread of sense of hunger via network effect
    for agent, _ in self.spotTaken:
      if agent.foodStock < agent.foodCRate:
        # step 2: calculate casualty
        agent.die()
        self.removeAgentFromSpot(agent)
        self.removeAgentFromMinistry(agent)
        self.diedAgent[CauseOfDeath.Hunger].append(agent)
        # step 3: spread sense of hunger
        self.spreadSenseOfHunger(agent)
      else:
        # step 1: Consume food
        agent.foodStock -= agent.foodCRate
    
    # Rebel spreading effect via network effect

    # Collect metrics and inner party make decisions on whether to adjust resources allocation
    metrics = {}
    metrics[Ministry.Plenty]=self.plentyMinistry.getMetricks()
    metrics[Ministry.Peace]=self.peaceMinistry.getMetricks()
    metrics[Ministry.Love]=self.loveMinistry.getMetricks()
    metrics[Ministry.Truth]=self.truthMinistry.getMetricks()

    # Inner party make decision
    self.ministryMembers = InnerParty.make_decision(metrics, self.ministryMembers)

    # Ministries renew their resources
    self.plentyMinistry.allocateNewResources(self.ministryMembers[Ministry.Plenty])
    self.peaceMinistry.allocateNewResources(self.ministryMembers[Ministry.Peace])
    self.loveMinistry.allocateNewResources(self.ministryMembers[Ministry.Love])
    self.truthMinistry.allocateNewResources(self.ministryMembers[Ministry.Truth])    

  def getRebelledAgentActivity(self):
     """
      Since the rebelled agent can do a varity of actions, and we decide to let the rebelled
      agent randomly choose one action at a time, since all the action also have possibilities
     """
     for rebelledOuterParty in self.rebeledAgents[Classes.OuterParty]:
        # here we assign the functionality of rebelled behaviour to the agent via the rebel variable
        outerPartyRebelActions = list(self.outer_party_probabilities.keys())
        outerPartyRebelWeights = list(self.outer_party_probabilities.values())
        rebelledOuterParty.rebel = random.choices(outerPartyRebelActions, weights=outerPartyRebelWeights, k=1)[0]
     
     for rebelledInnerParty in self.rebeledAgents[Classes.InnerParty]:
        # here we assign the functionality of rebelled behaviour to the agent via the rebel variable
        prolesRebelActions = list(self.prole_probabilities.keys())
        prolesRebelWeights = list(self.prole_probabilities.values())
        rebelledInnerParty.rebel = random.choices(prolesRebelActions, weights=prolesRebelWeights, k=1)[0]


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

        # Mark the spot as taken by the agent
        self.spotTaken.append([innerParty, (x, y)])
  

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
        self.spotTaken.append([outerParty, (x, y)])

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

        self.grid.place_agent(prole, (x, y))
        self.schedule.add(prole)

        # Mark the spot as taken
        self.spotTaken.append([prole, (x, y)])

  def spreadSenseOfSatefy(self, agent):
     """
      Spread the sense of safety via network effect
      Take account of truthMinistry to interfere with the spreading
     """
     pass

  def spreadSenseOfHunger(self, agent):
     """
      Spread the sense of hunger via network effect
      Take account of truthMinistry to interfere with the spreading
     """
     pass

  def removeAgentFromSpot(self, agent):
     """
      Remove the agent from spot
     """
     for i in range(len(self.spotTaken)):
        if self.spotTaken[i][0] == agent:
           break
     self.spotTaken.pop(i)
        

  def removeAgentFromMinistry(self, agent):
     """
      Remove the agent from its working ministry, excpet for inner party
     """
     if isinstance(agent, InnerParty):
        return
     if isinstance(agent, Proles):
        for i in range(len(self.ministryMembers[agent.ministry][Proles])):
           if self.ministryMembers[agent.ministry][Proles][i] == agent:
              break
        self.ministryMembers[agent.ministry][Proles].pop(i)
     elif isinstance(agent, OuterParty):
        for i in range(len(self.ministryMembers[agent.ministry][OuterParty])):
           if self.ministryMembers[agent.ministry][OuterParty][i] == agent:
              break
        self.ministryMembers[agent.ministry][OuterParty].pop(i)

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



