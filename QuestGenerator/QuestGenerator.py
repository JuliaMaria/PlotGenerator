# TODO Combine all parts of offline quest generator

from PlotGenerator.DomainDatabase.DomainDatabase import DomainDatabase
from PlotGenerator.QuestGenerator.GeneticAlgorithm import GeneticAlgorithm

dd = DomainDatabase("PlotGenerator/Domain/World.xml")
ga = GeneticAlgorithm(dd, population_size=5, mutation_prob=0.2, elitism_factor=0.2, start_size=(1, 10), goal_size=(1, 5))
quests_with_plans = ga(generations=1, num_quests=5, desired_story_arc=None)

for quest_with_plan in quests_with_plans:
    print(f"Start: {quest_with_plan[0][0]}")
    print(f"Goal: {quest_with_plan[0][1]}")
    print(f"Plan: {quest_with_plan[1]}")
