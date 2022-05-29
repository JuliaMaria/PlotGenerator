# TODO Combine all parts of offline quest generator
from PlotGenerator.DomainDatabase.DomainDatabase import DomainDatabase
from PlotGenerator.QuestGenerator.GeneticAlgorithm import GeneticAlgorithm

dd = DomainDatabase("PlotGenerator/Domain/World.xml")
ga = GeneticAlgorithm(dd)
quests_with_plans = ga(generations=5, num_quests=5)

for quest_with_plan in quests_with_plans:
    print(f"Start: {quest_with_plan[0][0]}")
    print(f"Goal: {quest_with_plan[0][1]}")
    print(f"Plan: {quest_with_plan[1]}")
