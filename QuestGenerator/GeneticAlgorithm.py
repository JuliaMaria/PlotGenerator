import itertools
import os
from collections import defaultdict
import re

import numpy as np
import subprocess
from tqdm import tqdm


class GeneticAlgorithm:
    def __init__(self, domain_database, population_size=100, mutation_prob=0.2, elitism_factor=0.2, start_size=(1, 31), goal_size=(1, 11), planner_folder="PlotGenerator/Planner"):
        self.population_size = population_size
        self.start_size = start_size
        self.goal_size = goal_size
        self.mutation_prob = mutation_prob
        self.elitism_factor = elitism_factor
        self.planner_folder = planner_folder

        self.dd = domain_database

    def generate_random_individual(self):
        # Choose how many objects to start with
        objects_start_size = np.random.randint(self.start_size[0], self.start_size[1])

        # Choose how many objects of different types to choose
        object_types_start_size = np.random.default_rng().multinomial(objects_start_size, [1 / len(self.dd.objects)] * len(self.dd.objects), size=1)[0]

        # Choose how many relations to start with
        max_relations_start_size = self.start_size[1]-objects_start_size if self.start_size[1]-objects_start_size > self.start_size[0] + 1 else self.start_size[0] + 1
        relations_start_size = np.random.randint(self.start_size[0], max_relations_start_size)

        # Choose how many relations to end with
        goal_size = np.random.randint(self.goal_size[0], self.goal_size[1])

        # Choose objects of the plot
        objects = {
            object_type: np.random.choice(self.dd.objects[object_type], object_type_size, replace=False)
            if object_type_size <= len(self.dd.objects[object_type]) else self.dd.objects[object_type]
            for object_type, object_type_size in zip(self.dd.objects.keys(), object_types_start_size)
        }
        all_objects = list(np.concatenate(list(objects.values())))

        # Filter valid relations for objects of the plot
        relations = [relation for relation in self.dd.relations if set(relation["values"]).issubset(all_objects)]

        # Choose start relations of the plot
        start_relations = list(np.random.choice(relations, relations_start_size, replace=False)) if relations_start_size <= len(relations) else relations

        # Filter valid predicates for objects of the plot
        predicates = [
            predicate
            for predicate in self.dd.predicates
            if np.all([len(objects[parameter["type"]]) for parameter in predicate["parameters"]])
               and predicate["attributes"]["goalstate"] == "true"
               and np.any([parameter["type"] == "character" for parameter in predicate["parameters"]])
        ]
        # Choose goal relations of the plot
        goal_predicates = list(np.random.choice(predicates, goal_size)) if goal_size <= len(predicates) else predicates
        goal_relations = [
            self.dd.relation_representation(predicate["name"], [np.random.choice(objects[parameter["type"]]) for parameter in predicate["parameters"]])
            for predicate in goal_predicates
        ]
        # Remove opposite relations for the same objects
        for relation in goal_relations:
            opposite_relation_name = [
                predicate["attributes"]["oposite"]
                for predicate in predicates
                if predicate["name"] == relation["name"] and "oposite" in predicate["attributes"]
            ]
            if opposite_relation_name:
                opposite_relation = self.dd.relation_representation(opposite_relation_name[0], relation["values"])
                if opposite_relation in goal_relations:
                    goal_relations.remove(opposite_relation)

        objects = [self.dd.object_representation(object_type, object) for object_type, objects_ in objects.items() for object in objects_]

        individual = [objects + start_relations, goal_relations]

        return individual

    def generate_initial_population(self):
        population = []
        for i in range(self.population_size):
            individual = self.generate_random_individual()
            population.append(individual)
        return population

    def perform_planning(self, individual):
        # Convert individual to PDDL format and save to file
        self.convert_individual_to_pddl_format(individual)

        # Run HSP planner
        subprocess.call(['sh', 'PlotGenerator/Planner/RunPlanner.sh'])

        # Remove file with individual
        os.remove(os.path.join(self.planner_folder, "Individual.pddl"))

        # Read solution from file
        with open('PlotGenerator/Planner/solutions.all', 'r') as file:
            solution = file.readlines()

        # Remove file with solution
        os.remove(os.path.join(self.planner_folder, "solutions.all"))

        return solution

    def convert_individual_to_pddl_format(self, individual, name="Individual"):
        # returns the resulting pddl filename
        filename = os.path.join(self.planner_folder, name + '.pddl')

        with open(filename, 'w') as f:
            f.write(f"(define (problem {name})")
            f.write(f"\n\t(:domain {self.dd.name})")

        # objects
        objects = [p for p in individual[0] if 'type' in p.keys()]

        with open(filename, 'a') as f:
            f.write("\n\t(:objects")

            for o in objects:
                f.write(f"\n\t\t{o['name']}")

            f.write("\n\t)")

        # preconditions
        preconditions = [p for p in individual[0] if 'values' in p.keys()]

        with open(filename, 'a') as f:
            f.write("\n\t(:init")

            for precondition in preconditions:
                f.write(f"\n\t\t({precondition['name']}")
                for v in precondition['values']:
                    f.write(f" {v}")
                f.write(")")

            f.write("\n\t)")

        # effects
        effects = individual[1]

        with open(filename, 'a') as f:
            f.write("\n\t(:goal")
            f.write("\n\t\t(and")

            for effect in effects:
                f.write(f"\n\t\t\t({effect['name']}")
                for v in effect['values']:
                    f.write(f" {v}")
                f.write(")")

            f.write("\n\t\t)")
            f.write("\n\t)")

            f.write("\n)")

        return filename

    def extract_actions_from_plan(self, solution):
        # Convert file with solutions to list of actions
        actions = []
        for line in solution:
            line = line.strip()
            if line.startswith("("):
                line = re.sub(r"[()]+", "", line)
                if line:
                    action = line.split()[0].lower()
                    actions.append(action)
        return actions

    def rescale_story_arc(self, story_arc, story_arc_scaling_factor):
        # Rescale story arc to length of scaling_factor
        # (index generated in range (1, story_arc_scaling_factor) as in the paper and lowered by 1 to match list indexing)
        scaled_story_arc = [
            story_arc[int(np.ceil((i-1)/story_arc_scaling_factor*(len(story_arc)-1))+1-1)]
            for i in range(1, story_arc_scaling_factor+1)
        ]
        return scaled_story_arc

    def evaluate_individual(self, individual, desired_story_arc, story_arc_scaling_factor=10):
        # Evaluate individual as described in the paper
        #  using HSP planner to generate actions for given start and goal
        #  and calculate fitness according to event effects from domain database

        # Generate plan for individual
        solution = self.perform_planning(individual)
        # Extract actions from plan
        actions = self.extract_actions_from_plan(solution)
        # Fitness is 0 for unsolvable individuals
        if not actions:
            return 0

        # Convert actions to tension arc
        tension_arc = [self.dd.event_effects[action] for action in actions]
        tension_arc = [sum(tension_arc[:i+1]) for i in range(len(tension_arc))]

        # Rescale both story arcs to common time frame
        scaled_desired_arc = self.rescale_story_arc(desired_story_arc, story_arc_scaling_factor)
        scaled_tension_arc = self.rescale_story_arc(tension_arc, story_arc_scaling_factor)

        # Calculate loss between two story arcs
        mse = sum([(tension_p-tension_d)**2 for tension_p, tension_d in zip(scaled_tension_arc, scaled_desired_arc)])/story_arc_scaling_factor
        fitness = len(tension_arc)/mse

        return fitness

    def evaluate_population(self, population, desired_story_arc):
        # Evaluate population according to their story arcs and desired story arc
        evaluated_population = []
        for individual in population:
            evaluated_population.append(
                {
                    "individual": individual,
                    "fitness": self.evaluate_individual(individual, desired_story_arc)
                }
            )
        return evaluated_population

    def remove_invalid_relations(self, individual):
        # Remove relations in individual that don't match objects of its plot
        objects = []
        for literal in individual[0]:
            if "type" in literal.keys():
                objects.append(literal["name"])

        for literal in individual[0]:
            if "values" in literal.keys():
                for value in literal["values"]:
                    if value not in objects:
                        individual[0].remove(literal)
                        break

        for literal in individual[1]:
            if "values" in literal.keys():
                for value in literal["values"]:
                    if value not in objects:
                        individual[1].remove(literal)
                        break

        return individual

    def perform_crossover(self, selected_individuals):
        # Select pairs of individuals for reproduction at random
        all_pairs = list(itertools.combinations_with_replacement(selected_individuals, 2))
        # Each pair produces two children so we take self.population_size//2 pairs
        pairs_to_reproduce_idxs = np.random.choice(len(all_pairs), self.population_size//2, replace=False)
        pairs_to_reproduce = [all_pairs[idx] for idx in pairs_to_reproduce_idxs]

        new_population = []

        for individual_1, individual_2 in pairs_to_reproduce:
            # Select split points for start and goal according to length of shortest parent
            individual_1 = individual_1["individual"]
            individual_2 = individual_2["individual"]
            smallest_individual_start_length = min(len(individual_1[0]), len(individual_2[0]))
            smallest_individual_goal_length = min(len(individual_1[1]), len(individual_2[1]))
            start_split_point = np.random.randint(0, smallest_individual_start_length - 1) if smallest_individual_start_length - 1 > 0 else 0
            goal_split_point = np.random.randint(0, smallest_individual_goal_length - 1) if smallest_individual_goal_length - 1 > 0 else 0

            # Generate offspring
            child_1 = [
                individual_1[0][:start_split_point] + individual_2[0][start_split_point:],
                individual_1[1][:goal_split_point] + individual_2[1][goal_split_point:]
            ]

            child_2 = [
                individual_2[0][:start_split_point] + individual_1[0][start_split_point:],
                individual_2[1][:goal_split_point] + individual_1[1][goal_split_point:]
            ]

            child_1 = self.remove_invalid_relations(child_1)
            child_2 = self.remove_invalid_relations(child_2)

            new_population.append(child_1)
            new_population.append(child_2)

        return new_population

    def add_literal_to_individual(self, individual, target):
        # Target: 0 - start, 1 - goal, 2 - both
        # Get objects of the plot
        objects = defaultdict(list)
        for literal in individual[0]:
            if "type" in literal.keys():
                objects[literal["type"]].append(literal["name"])

        # Filter valid predicates for objects of the plot
        predicates = [
            predicate
            for predicate in self.dd.predicates
            if np.all([len(objects[parameter["type"]]) for parameter in predicate["parameters"]])
        ]

        # If no literals can be added, return unchanged individual
        if not predicates:
            return individual

        if target in [0, 2]:
            # Choose start relation of the plot
            start_predicate = np.random.choice(predicates)
            start_relation = self.dd.relation_representation(start_predicate["name"], [np.random.choice(objects[parameter["type"]]) for parameter in start_predicate["parameters"]])
            individual[0].append(start_relation)
        if target in [1, 2]:
            # Choose goal relation of the plot
            goal_predicate = np.random.choice(predicates)
            goal_relation = self.dd.relation_representation(goal_predicate["name"], [np.random.choice(objects[parameter["type"]]) for parameter in goal_predicate["parameters"]])
            individual[1].append(goal_relation)

        return individual

    def remove_literal_from_individual(self, individual, target):
        # Target: 0 - start, 1 - goal, 2 - both
        if target in [0, 2]:
            # Don't remove objects from individual, only relations
            possible_literals_to_remove = [literal for literal in individual[0] if "type" not in literal.keys()]
            if possible_literals_to_remove:
                literal_to_remove = np.random.choice(possible_literals_to_remove)
                individual[0].remove(literal_to_remove)
        if target in [1, 2]:
            # Don't remove objects from individual, only relations
            possible_literals_to_remove = [literal for literal in individual[1] if "type" not in literal.keys()]
            if possible_literals_to_remove:
                literal_to_remove = np.random.choice(possible_literals_to_remove)
                individual[1].remove(literal_to_remove)
        return individual

    def perform_mutation(self, population):
        new_population = []

        for individual in population:
            if np.random.rand() < self.mutation_prob:
                # Start, goal or both
                mutation_target = np.random.choice(3)
                # Add, remove or both
                mutation_type = np.random.choice(3)

                if mutation_type in [0, 2]:
                    individual = self.add_literal_to_individual(individual, mutation_target)
                if mutation_type in [1, 2]:
                    individual = self.remove_literal_from_individual(individual, mutation_target)

            new_population.append(individual)

        return new_population

    def select_best_individuals(self):
        # Select elite individuals for next generation and select other individuals for next generation at random
        # according to their fitness
        elite_individuals_to_copy = int(self.elitism_factor*self.population_size)
        sorted_individuals = sorted(self.population, key=lambda x: x["fitness"], reverse=True)

        elite_individuals = sorted_individuals[:elite_individuals_to_copy]
        remaining_individuals = sorted_individuals[elite_individuals_to_copy:]

        max_sum = sum([individual["fitness"] for individual in remaining_individuals])
        if max_sum != 0:
            selection_probs = [individual["fitness"] / max_sum for individual in remaining_individuals]
        else:
            selection_probs = [1 / len(remaining_individuals) for individual in remaining_individuals]

        chosen_remaining_individuals = [
            remaining_individuals[idx]
            for idx in np.random.choice(len(remaining_individuals), p=selection_probs, size=self.population_size-elite_individuals_to_copy)
        ]

        return elite_individuals + chosen_remaining_individuals

    def __call__(self, generations, num_quests, desired_story_arc):
        # Generate quests according to algorithm schema from paper
        quests = []

        for quest in tqdm(range(num_quests)):
            population = self.generate_initial_population()
            self.population = self.evaluate_population(population, desired_story_arc)

            for generation in range(generations):
                best_individuals = self.select_best_individuals()
                population = self.perform_crossover(best_individuals)
                population = self.perform_mutation(population)
                population = [self.remove_invalid_relations(individual) for individual in population]
                self.population = self.evaluate_population(population, desired_story_arc)

            best_quest = max(self.population, key=lambda x: x["fitness"])
            quests.append(best_quest["individual"])

        quests_with_plans = [(quest, self.perform_planning(quest)) for quest in quests]

        return quests_with_plans
