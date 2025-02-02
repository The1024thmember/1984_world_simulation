
import numpy as np
from Common import Classes, RebelProleActions


class PlentyMinistry():
  """
  Labour: 
    - Inner party: decision making on allocating resources of OuterParty and Proles
    - Outer party: ensure food distruibution efficiency via network diffusion
    - Proles: produce food

  Function: 
    - Collecting and distruibute food to every agents

  Metricks:
    - The number of agents died from hunger
    - The delta of metricks from last step to current step
  """
  def __init__(self,
               proles, # a list of prole that work for peace that work for peace ministry
               outerParties, # a list of outer party that work for peace ministry
               nInnerParty, # number of inner party
               diffusionRate, # Percentage of food to distribute to neighbors
               varianceThreshold, # Variance threshold to determine convergence
              ):
    self.proles = proles
    self.outerParties = outerParties
    self.nInnerParty = nInnerParty
    self.numberOfDiedAgents = 0
    self.diffusionRate = diffusionRate
    self.varianceThreshold = varianceThreshold
    pass

  def generateAndDistributeFood(self, agentsSpot, gridSize):
    """
      Locate the proles location, generate food on this location
      Use network diffusion, distribute food to every agent based on their location
      Agents then put the newly distruibuted food into their stock for consumption

      Keep in mind that this function should take the number of OuterParty and rebel 
      and etc as input, as it impacts the food generation and distruibution process
    """
    def diffuse(variance):
      """
      Recursive diffusion process to ensure global low variance.
      Spreading is restricted to agentsPosition.
      """
      changes_made = False  # Track if any changes occur in this step
      new_grid = np.zeros_like(foodGrid)  # Food will only exist in y_positions
      for i, j in agentsPosition:
          if foodGrid[i, j] > 0:  # Consider only cells with food
              neighbors = [(ni, nj) for ni in range(max(0, i-1), min(gridSize, i+2))
                          for nj in range(max(0, j-1), min(gridSize, j+2))
                          if (ni, nj) != (i, j) and (ni, nj) in agentsPosition]
              for ni, nj in neighbors:
                  if foodGrid[i, j] > foodGrid[ni, nj]:  # Spread only if current cell is greater
                      transfer = self.diffusionRate * (foodGrid[i, j] - foodGrid[ni, nj])  # Spread proportionally
                      new_grid[ni, nj] += transfer
                      new_grid[i, j] -= transfer
                      changes_made = True

      # Add the remaining unchanged food values back to new_grid
      for i, j in agentsPosition:
          new_grid[i, j] += foodGrid[i, j]

      # If no changes were made, grid has stabilized
      if not changes_made:
          return new_grid

      # Check variance among y_positions
      currentV = np.var([new_grid[i, j] for i, j in agentsPosition])
      if currentV < variance:
          return new_grid  # Stop if variance is below threshold
      else:
          return diffuse(new_grid, agentsPosition)  # Recurse otherwise


    # virtue food grid for collecting and distruting food
    foodGrid = []

    # get agent position
    agentsPosition = [each[0] for each in agentsSpot]

    # food generation
    for each in self.proles:
      if each.rebel == RebelProleActions.Misfunction:
        # produce much less food than normal
        foodGrid[each.pos[0]][each.pos[1]]=each.foodPRate * 0.1
      else:
        foodGrid[each.pos[0]][each.pos[1]]=each.foodPRate

    # food distruibution, take the number of rebelled outer party into account
    for each in self.outerParties:
      if each.rebel == RebelProleActions.Misfunction:
        # the more rebelled outerParty, the higher value for varianceThreshold
        variance += 2
    distributed =  diffuse(variance)

    # allocate food to agents
    for [agent,_] in agentsPosition:
       agent.foodStock += distributed[agent.pos[0]][agent.pos[1]]


  def getMetricks(self):
    """
      Collect the number of agents died because of hunger in this round
      Calculate the delta
    """
    pass

  
  def allocateNewResources(self, resources):
    """
      Allocate new resources for this ministry
    """
    self.proles = resources[Classes.Proles]
    self.outerParties = resources[Classes.OuterParty]

    