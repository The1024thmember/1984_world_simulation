### Mesa version = 3.0.3
import mesa
import warnings

from Common import CauseOfDeath, Classes, Ministry

# Suppress all UserWarnings, there are some UserWarning and DeprecationWarning
# which spamming the terminal
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class InnerParty(mesa.Agent):
  """
    InnerParty:
    - Make decisions requested from the 4 ministries
    - Takes 2% of population
    - They don't really have the Maslow's pyramid need as they symbolizes the party, not real human
  """
  # Here we use class level variable since population belongs to this class
  population = 2

  def __init__(self,
              model,
              pos, # current position
              alive, # is alive
              foodCRate, # food consumption rate
              foodStock, # the current food holding
              ):
    super().__init__(model)
    self.model = model
    self.pos = pos
    self.alive = alive
    self.foodCRate = foodCRate
    self.foodStock = foodStock

  """
    Inner party member can die from two ways:
    - bomb attack
    - hunger

    remove from the grid, reduce the number of InnerParty in All ministries
  """
  def die(self, cause):
    self.alive = False
    self.model.grid.remove_agent(self)
    self.model.schedule.remove(self)
    if cause == CauseOfDeath.Hunger:
      self.spreadSenseOfHunger()
      self.model.plentyMinistry.numberOfDiedAgents[1]+=1
    elif cause == CauseOfDeath.BombAttack:
      self.spreadSenseOfSatefy()
      self.model.numberOfDiedAgents.numberOfDiedAgents[1]+=1

  def consumeFood(self):
    """
    # Food consumption
    # 1. Consume food
    """    
    if self.foodStock < self.foodCRate:
      self.die()

  """
    Here we use class method, since the function execution is on the InnerParty level
    not for each individual, as long as there is at least 1 inner party survive, the 
    its power still exsits.

    make decision based on request
  """
  @classmethod
  def step(cls, request):
    if cls.population < 1:
      print("*********************************************************")
      print("------------------ BIG BROTHER IS DEAD ------------------")
      print("*********************************************************")
      exit()
    # Based on the request, make the decision
    cls.make_decision(cls, request)
    
  """
    Based on the performance of four ministries, allocating ourterparty and prole resources to
    the four ministries.
  """  
  @classmethod
  def make_decision(cls, metrics, existingMinistryMembers):
    """
    Inner Party makes decisions on shifting resources between ministries
    based on collected metrics and current ministry staffing.

    Inner Party reallocates resources based on normalized ministry metrics.
    Prioritization Order:
    1. Ministry of Peace
    2. Ministry of Plenty
    3. Ministry of Love
    4. Ministry of Truth
    """
    new_allocation = {
        Ministry.Love: {Classes.OuterParty: []},
        Ministry.Truth: {Classes.OuterParty: []},
        Ministry.Plenty: {Classes.OuterParty: [], Classes.Proles: []},
        Ministry.Peace: {Classes.OuterParty: [], Classes.Proles: []}
    }


    # Step 1: Extract key metrics
    love_metric = metrics[Ministry.Love]
    truth_metric = metrics[Ministry.Truth]
    plenty_metric = metrics[Ministry.Plenty]
    peace_metric = metrics[Ministry.Peace]

    # Step 2: Define Normalization Ranges (Using Past Max Values)
    min_max_ranges = {
        Ministry.Love: (0, max(20, existingMinistryMembers[Ministry.Love][1])),
        Ministry.Truth: (0, max(15, existingMinistryMembers[Ministry.Truth][1])),
        Ministry.Plenty: (0, max(30, existingMinistryMembers[Ministry.Plenty][1])),
        Ministry.Peace: (0, max(20, existingMinistryMembers[Ministry.Peace][1]))
    }
    
    # **Step 3: Normalize Metrics Between [0,1]**
    normalized_scores = {
        Ministry.Love: cls.normalize_metric(sum(love_metric), *min_max_ranges[Ministry.Love]),
        Ministry.Truth: cls.normalize_metric(sum(truth_metric), *min_max_ranges[Ministry.Truth]),
        Ministry.Plenty: cls.normalize_metric(sum(plenty_metric), *min_max_ranges[Ministry.Plenty]),
        Ministry.Peace: cls.normalize_metric(sum(peace_metric), *min_max_ranges[Ministry.Peace])
    }

    # **Step 4: Apply Weighted Prioritization**
    priority_weights = {
        Ministry.Peace: 1.0,  # Highest priority (prevents deaths from bomb attacks)
        Ministry.Plenty: 0.8,  # Second priority (hunger can kill)
        Ministry.Love: 0.6,  # Controls rebels (who can kill)
        Ministry.Truth: 0.4   # Least urgent (long-term rebel suppression)
    }

    # Adjust weights based on real-time severity
    weighted_scores = {ministry: normalized_scores[ministry] * priority_weights[ministry] for ministry in normalized_scores}
    
    # Normalize weights to make them proportional
    total_weight = sum(weighted_scores.values())
    allocation_ratios = {ministry: weighted_scores[ministry] / total_weight if total_weight > 0 else 0 for ministry in weighted_scores}

    # Step 5: Distribute Available Agents Based on Weighted Allocation
    outer_party_agents = []
    prole_agents = []
    
    for ministry in existingMinistryMembers:
        for agent in existingMinistryMembers[ministry][Classes.OuterParty]:
            outer_party_agents.append(agent)
        if Classes.Proles in existingMinistryMembers[ministry]:
            for agent in existingMinistryMembers[ministry][Classes.Proles]:
                prole_agents.append(agent)

    # Step 6: Allocate Agents by Class to Ministries That Accept Them
    ministry_buckets = {m: {Classes.OuterParty: [], Classes.Proles: []} for m in new_allocation}

    for agent in outer_party_agents:
        target_ministry = max(allocation_ratios, key=lambda m: allocation_ratios[m])
        if Classes.OuterParty in new_allocation[target_ministry]:  # Only assign if valid
            ministry_buckets[target_ministry][Classes.OuterParty].append(agent)

    for agent in prole_agents:
        target_ministry = max(allocation_ratios, key=lambda m: allocation_ratios[m])
        if Classes.Proles in new_allocation[target_ministry]:  # Only assign if valid
            ministry_buckets[target_ministry][Classes.Proles].append(agent)

    # Step 7: Assign Agents to Ministries
    for ministry, agent_groups in ministry_buckets.items():
        new_allocation[ministry][Classes.OuterParty].extend(agent_groups[Classes.OuterParty])
        if Classes.Proles in new_allocation[ministry]:  # Assign Proles only where needed
            new_allocation[ministry][Classes.Proles].extend(agent_groups[Classes.Proles])

    return new_allocation

