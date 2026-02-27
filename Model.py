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
      initialPopulation = 200, # initial population
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

    self.initialPopulation = initialPopulation
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
    # All the agents
    self.spotTaken = []

    # avaliable spots for agents 
    self.available_spots = [(x, y) for x in range(width) for y in range(height)]  # Pre-generate all (x, y)
    random.shuffle(self.available_spots)
    
    # The agents that died in current step
    # self.diedAgent = {}
    # for cause in CauseOfDeath:
    #    self.diedAgent[cause.name] = []

    # The rebelled agents
    # self.rebeledAgents = {
    #    Classes.OuterParty:[],
    #    Classes.Proles:[]
    # }


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

    self.initialPopulation = initialPopulation

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

    self.death_counts = {cause: 0 for cause in CauseOfDeath}

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

    # Determine if agent is rebel or not
    for each in self.spotTaken:
      if isinstance(each, (OuterParty, Proles)):
        each.rebel = each.loyalty < 50

    # Get rebelled agent activity
    self.getRebelledAgentActivity()

    # Food production, the proles produces food, then get distruibuted
    self.plentyMinistry.generateAndDistributeFood(self.spotTaken, gridSize = (self.width, self.height))

    # Weapon production
    self.peaceMinistry.collectWeapons()

    # Bomb attack, it is a rare event
    # 1. Defend bomb attack
    # 2. Calculate Casualty
    # 3. Spread of sense of safety via network effect
    if self.bomb.should_attack():
      # step 1: defend bomb attack
      attackedLocation = self.peaceMinistry.defendBombAttack(self.bomb)
      for pos in attackedLocation:
        this_cell = self.grid.get_cell_list_contents(pos)
        for agent in this_cell:
          # need to ensure the agent is removed from the ministry as well
          if isinstance(agent, (Proles, OuterParty, InnerParty)):
            # step 2: calculate casualty
            agent.die(CauseOfDeath.BombAttack)

    # Consume food
    for agent in self.spotTaken:
      agent.consumeFood()
    
    # Rebel spreading effect via network effect, monitored by love ministry
    for each in self.spotTaken:
      if each.rebel:
        each.rebelSpread()

    # Calculate the loyalty score for every agent, the loyalty is the 
    # combination of sense of hunger and sense of safety, to retain the effect
    # of increase loyalty, the current loyalty is based on existing value + new sensory
    for each in self.spotTaken:
      if isinstance(each, (OuterParty, Proles)):
         each.loyalty = compute_loyalty(each.loyalty, each.senseOfHunger, each.senseOfSafety)

    # Truth ministry help in increasing loyalty score
    self.truthMinistry.increaseLoyaltyScore(self.spotTaken)

    # Rebelled agent take action to kill other agents
    for each in self.spotTaken:
      targetAgent = None
      if each.rebel_action == RebelProleActions.KillOuterParty:
        targetAgent = self.getRandomOuterParty(exclude=each)
      elif each.rebel_action == RebelProleActions.KillProle:
        targetAgent = self.getRandomProle(exclude=each)
      elif each.rebel_action == RebelOuterPartyActions.KillOuterParty:
        targetAgent = self.getRandomOuterParty(exclude=each)
      elif each.rebel_action == RebelOuterPartyActions.KillProle:
        targetAgent = self.getRandomProle(exclude=each)
      if targetAgent is not None:
        targetAgent.die(CauseOfDeath.Murder)

    # Love ministry executes or transform caught rebelled agents
    self.loveMinistry.processRebelCase()

    # Refresh the alive agent
    for each in list(self.spotTaken):
       if not each.alive:
        self.removeAgentFromMinistry(each)
    self.spotTaken = [each for each in self.spotTaken if each.alive]
    
    # Collect metrics and inner party make decisions on whether to adjust resources allocation
    # We assume that the agent will still perform their job during the step when they were dead
    metrics = {}
    metrics[Ministry.Plenty]=self.plentyMinistry.getMetricks()
    metrics[Ministry.Peace]=self.peaceMinistry.getMetricks()
    metrics[Ministry.Love]=self.loveMinistry.getMetricks()
    metrics[Ministry.Truth]=self.truthMinistry.getMetricks(self.spotTaken)

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
     for each in self.spotTaken:
        if each.rebel:
          if isinstance(each, OuterParty):
            outerPartyRebelActions = list(self.outer_party_probabilities.keys())
            outerPartyRebelWeights = list(self.outer_party_probabilities.values())
            each.rebel_action = random.choices(outerPartyRebelActions, weights=outerPartyRebelWeights, k=1)[0]
          elif isinstance(each, Proles):
            prolesRebelActions = list(self.prole_probabilities.keys())
            prolesRebelWeights = list(self.prole_probabilities.values())
            each.rebel_action = random.choices(prolesRebelActions, weights=prolesRebelWeights, k=1)[0]
        else:
          each.rebel_action = None

  def initializeInnerParty(self):
    # Initialize InnerParty
    self.numberOfInnerParty = int(round(self.agentDistribution[Classes.InnerParty]*self.initialPopulation))
    for i in range(self.numberOfInnerParty):
        # Find a unique spot for the InnerParty agent
        x,y = self.findSpot()

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
        self.spotTaken.append(innerParty)
  

  def initalizeOuterParty(self):
    # Initialize OuterParty
    numberOfOuterParty = int(round(self.agentDistribution[Classes.OuterParty]*self.initialPopulation))
    outerPartyMinistryDistribution = get_ministry_distribution(self.ministryResourcesDistribution, Classes.OuterParty)
    
    for i in range(numberOfOuterParty):
        # Find a unique spot for the OuterParty agent
        x,y = self.findSpot()

        # get the ministry for outer party
        ministry = choose_ministry(outerPartyMinistryDistribution)

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
        outerParty.rebel_action = None
        # put the outer party into certain ministry
        self.ministryMembers[ministry][Classes.OuterParty].append(outerParty)
            
        self.grid.place_agent(outerParty, (x, y))
        self.schedule.add(outerParty)

        # Mark the spot as taken
        self.spotTaken.append(outerParty)

  def initializeProles(self):
    # Initialize Proles
    numberOfProles = self.initialPopulation - int(round(self.agentDistribution[Classes.InnerParty]*self.initialPopulation)) - int(round(self.agentDistribution[Classes.OuterParty]*self.initialPopulation))
    prolesMinistryDistribution = get_ministry_distribution(self.ministryResourcesDistribution, Classes.Proles)

    for i in range(numberOfProles):
        # Find a unique spot for the Prole agent
        x,y = self.findSpot()

        ministry = choose_ministry(prolesMinistryDistribution)
       
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
        prole.rebel_action = None

        # put the proles into certain ministry
        self.ministryMembers[ministry][Classes.Proles].append(prole)

        self.grid.place_agent(prole, (x, y))
        self.schedule.add(prole)

        # Mark the spot as taken
        self.spotTaken.append(prole)

  def getRandomOuterParty(self, exclude=None):
    """
      Get a random outerparty member to be murdured by rebelled agent
    """
    candidates = [agent for agent in (self.loveMinistry.outerParties + self.truthMinistry.outerParties + self.peaceMinistry.outerParties + self.plentyMinistry.outerParties) if agent.alive and agent is not exclude]
    if not candidates:
      return None
    return random.choice(candidates)

  def getRandomProle(self, exclude=None):
    """
      Get a random prole member to be murdured by rebelled agent
    """
    candidates = [agent for agent in (self.peaceMinistry.proles + self.plentyMinistry.proles) if agent.alive and agent is not exclude]
    if not candidates:
      return None
    return random.choice(candidates)

  def removeAgentFromMinistry(self, agent):
     """
      Remove the agent from its working ministry, excpet for inner party
     """
     if isinstance(agent, InnerParty):
        return
     if isinstance(agent, Proles):
        members = self.ministryMembers[agent.ministry][Classes.Proles]
        if agent in members:
          members.remove(agent)
     elif isinstance(agent, OuterParty):
        members = self.ministryMembers[agent.ministry][Classes.OuterParty]
        if agent in members:
          members.remove(agent)

  def getFoodConsumeRate(self, minConsumption, maxConsumption):
    """
    Return a normal distruibution sampled food consumption rate
    """
    return self.random.uniform(minConsumption, maxConsumption)

  def getFoodProductionRate(self, minProduction, maxProduction):
    """
    Return a normal distruibution sampled food production rate
    """
    return self.random.uniform(minProduction, maxProduction)

  def getWeaponProductionRate(self, minProduction, maxProduction):
    """
    Return a normal distruibution sampled weapon production rate
    """
    return self.random.uniform(minProduction, maxProduction)

  def findSpot(self):
    """ Efficiently finds a free (x, y) location by removing from the pre-generated list. """
    if not self.available_spots:
        raise ValueError("No available spots left on the grid!")  # Handle full grid scenario
    
    new_spot = self.available_spots.pop()  # Take a random available spot
    return new_spot
    
  def releaseSpot(self, pos):
    if pos not in self.available_spots:
        self.available_spots.append(pos)
    else:
      raise ValueError("Release spot failed, spot already exist")

  def record_death(self, cause):
    if cause in self.death_counts:
      self.death_counts[cause] += 1

  def snapshot(self, step):
    agents = []
    for agent in self.spotTaken:
      if agent.pos is None:
        continue
      agents.append({
        "x": agent.pos[0],
        "y": agent.pos[1],
        "type": agent.__class__.__name__,
        "rebel": bool(getattr(agent, "rebel", False)),
      })
    return {
      "step": step,
      "agents": agents,
      "width": self.width,
      "height": self.height,
    }

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
    for ministry, allocation in ministryResourcesDistribution.items():
        if class_type in allocation:
            distribution_range[ministry] = allocation[class_type]
    return distribution_range


def choose_ministry(ministry_weights):
    ministries = list(ministry_weights.keys())
    weights = [max(0, ministry_weights[m]) for m in ministries]
    if sum(weights) == 0:
        return random.choice(ministries)
    return random.choices(ministries, weights=weights, k=1)[0]


def compute_loyalty(current, sense_of_hunger, sense_of_safety):
  hunger_penalty = min(100, max(0, sense_of_hunger))
  safety_penalty = min(100, max(0, sense_of_safety))
  base = 100 - ((hunger_penalty + safety_penalty) / 2)
  loyalty = (current * 0.6) + (base * 0.4)
  return max(0, min(100, loyalty))
