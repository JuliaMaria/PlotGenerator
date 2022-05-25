
class GeneticAlgorithm:
    def __init__(self, population_size, start_size, goal_size):
        self.population_size = population_size
        self.start_size = start_size
        self.goal_size = goal_size
        self.population = self.generate_initial_population()

    def generate_initial_population(self):
        return []

    def evaluate_individual(self, individual):
        return 0
