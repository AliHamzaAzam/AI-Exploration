#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/03/2025
#

import random
import pandas as pd

class ShelfOptimization:
    def __init__(self, shelves, products, POPULATION_SIZE=100, GENERATIONS=500, MUTATION_RATE=0.1):
        self.shelves = shelves
        self.products = products
        self.shelf_keys = list(shelves.keys())
        self.product_keys = list(products.keys())
        self.POPULATION_SIZE = POPULATION_SIZE
        self.GENERATIONS = GENERATIONS
        self.MUTATION_RATE = MUTATION_RATE

    ### Genetic Algorithm Functions ###
    # Individual Representation (Genes)
    # Gene : Product Key -> Shelf Key
    def create_individual(self):
        """Generate a random assignment: each product is assigned a random shelf."""
        return {p: random.choice(self.shelf_keys) for p in self.product_keys}

    def fitness(self, individual):
        """Calculate penalty score (lower is better). Zero means all constraints are satisfied."""
        penalty = 0
        shelf_weight = {s: 0 for s in self.shelf_keys}
        category_shelves = {}
        refrigerated_shelves = set()

        for p, shelf in individual.items():
            product = products[p]
            shelf_info = shelves[shelf]

            shelf_weight[shelf] += product['weight']
            category_shelves.setdefault(product['category'], set()).add(shelf)

            # Check perishable items
            if product['perishable']:
                if shelf_info['type'] != 'refrigerated':
                    penalty += 5
                refrigerated_shelves.add(shelf)
            else:
                if shelf_info['type'] == 'refrigerated':
                    penalty += 50

            # Check hazardous product storage
            if product['hazardous'] and shelf_info['type'] != 'hazardous':
                penalty += 10

            # Check high-demand product placement
            if product['high_demand'] and shelf_info.get('accessibility', 0) < 7:
                penalty += 5

            # Check promotional item placement
            if product.get('promotional', False) and shelf_info.get('accessibility', 0) < 7:
                penalty += 5

            # Check luxury/theft-prone items
            if product.get('luxury', False) and shelf_info.get('visibility', 0) < 7:
                penalty += 5

        # 1. Check shelf weight constraints
        for shelf, weight in shelf_weight.items():
            if weight > shelves[shelf]['capacity']:
                penalty += (weight - shelves[shelf]['capacity']) * 10  # Overweight penalty

        # 2. Check category grouping
        for category, shelf_set in category_shelves.items():
            if len(shelf_set) > 1:
                penalty += 10

        # 3. Complementary products (e.g., Pasta & Pasta Sauce should be together)
        if individual['P5'] != individual['P6']:
            penalty += 5

        # 4. Refrigeration efficiency
        if refrigerated_shelves:
            sorted_refrigerated = sorted(refrigerated_shelves, key=lambda s: shelf_weight[s], reverse=True)
            for s in sorted_refrigerated[1:]:
                if shelf_weight[s] > 0:
                    penalty += 1

        return penalty

    def selection(self, population):
        """Rank-based selection for better convergence."""
        population.sort(key=lambda individual: self.fitness(individual))
        return population[:2]

    def crossover(self, parent1, parent2):
        """Single-point crossover."""
        crossover_point = random.randint(1, len(self.product_keys) - 1)
        child1, child2 = {}, {}
        for i, p in enumerate(self.product_keys):
            child1[p] = parent1[p] if i < crossover_point else parent2[p]
            child2[p] = parent2[p] if i < crossover_point else parent1[p]
        return child1, child2

    def mutate(self, individual, mutation_rate):
        """Mutation: Randomly reassign a shelf with decreasing probability."""
        if random.random() < mutation_rate:
            p = random.choice(self.product_keys)
            individual[p] = random.choice(self.shelf_keys)
        return individual

    def optimize_shelves(self):
        """Genetic algorithm to optimize product placement on shelves."""
        # Generate initial population
        population = [self.create_individual() for _ in range(self.POPULATION_SIZE)]

        # Evolution loop
        for _ in range(self.GENERATIONS):
            # Selection
            parents = self.selection(population)

            # Crossover
            offspring = []
            for _ in range(self.POPULATION_SIZE - 2):
                offspring.extend(self.crossover(*random.sample(parents, 2)))

            # Mutation
            population = [self.mutate(child, self.MUTATION_RATE) for child in offspring]

        # Find the best individual
        best_individual = min(population, key=lambda ind: self.fitness(ind))
        return best_individual

    def get_optimized_shelves(self):
        return self.optimize_shelves()

    def print_optimized_shelves(self):
        print("Optimized Shelf Assignments:")
        print("----------------------------")
        print("Fitness Score:", self.fitness(self.get_optimized_shelves()))
        print("----------------------------")
        shelves_to_products = {}
        for product_key, shelf_key in optimized_shelves.items():
            if shelf_key not in shelves_to_products:
                shelves_to_products[shelf_key] = []
            shelves_to_products[shelf_key].append(product_key)

        # Print products grouped by shelf
        for shelf_key, product_keys in shelves_to_products.items():
            product_names = [products[p]['name'] for p in product_keys]
            total_weight = sum(products[p]['weight'] for p in product_keys)
            print(f"{shelf_key} ({shelves[shelf_key]['name']}): {', '.join(product_names)} ({total_weight}kg)")

    def store_in_xlsx(self):
        shelves_to_products = {}
        for product_key, shelf_key in optimized_shelves.items():
            if shelf_key not in shelves_to_products:
                shelves_to_products[shelf_key] = []
            shelves_to_products[shelf_key].append(product_key)

        data = []
        for shelf_key, product_keys in shelves_to_products.items():
            product_names = [products[p]['name'] for p in product_keys]
            total_weight = sum(products[p]['weight'] for p in product_keys)
            data.append([shelf_key, shelves[shelf_key]['name'], ', '.join(product_names), total_weight])

        df = pd.DataFrame(data, columns=['Shelf Key', 'Shelf Name', 'Products', 'Total Weight (kg)'])
        df.to_excel("optimized_shelf_assignments.xlsx", index=False)



### Main Code to Test the ShelfOptimization Class ###
if __name__ == "__main__":
    # Define shelves with properties
    shelves = {
        'S1': {'name': 'Checkout Display'   , 'capacity': 8 , 'type': 'general'     , 'accessibility': 15, 'visibility': 10},
        'S2': {'name': 'Lower Shelf'        , 'capacity': 25, 'type': 'general'     , 'accessibility': 1 , 'visibility': 6 },
        'S4': {'name': 'Eye-Level Shelf'    , 'capacity': 15, 'type': 'high_access' , 'accessibility': 10, 'visibility': 8 },
        'S5': {'name': 'General Aisle Shelf', 'capacity': 20, 'type': 'general'     , 'accessibility': 6 , 'visibility': 4 },
        'R1': {'name': 'Refrigerator Zone'  , 'capacity': 20, 'type': 'refrigerated', 'accessibility': 4 , 'visibility': 5 },
        'H1': {'name': 'Hazardous Zone'     , 'capacity': 10, 'type': 'hazardous'   , 'accessibility': 3 , 'visibility': 3 }
    }

    # Define products with properties
    products = {
        'P1': {'name': 'Milk'           , 'weight': 5 , 'category': 'dairy'     , 'high_demand': True , 'perishable': False, 'hazardous': False},
        'P2': {'name': 'Rice Bag'       , 'weight': 10, 'category': 'grains'    , 'high_demand': False, 'perishable': False, 'hazardous': False},
        'P3': {'name': 'Frozen Nuggets' , 'weight': 5 , 'category': 'frozen'    , 'high_demand': False, 'perishable': True , 'hazardous': False},
        'P4': {'name': 'Cereal'         , 'weight': 3 , 'category': 'breakfast' , 'high_demand': True , 'perishable': False, 'hazardous': False},
        'P5': {'name': 'Pasta'          , 'weight': 2 , 'category': 'grains'    , 'high_demand': False, 'perishable': False, 'hazardous': False},
        'P6': {'name': 'Pasta Sauce'    , 'weight': 3 , 'category': 'sauces'    , 'high_demand': False, 'perishable': False, 'hazardous': False},
        'P7': {'name': 'Detergent'      , 'weight': 4 , 'category': 'cleaning'  , 'high_demand': False, 'perishable': False, 'hazardous': True },
        'P8': {'name': 'Glass Cleaner'  , 'weight': 5 , 'category': 'cleaning'  , 'high_demand': False, 'perishable': False, 'hazardous': True }
    }

    shelf_optimizer = ShelfOptimization(shelves, products)
    optimized_shelves = shelf_optimizer.get_optimized_shelves()
    shelf_optimizer.print_optimized_shelves()
    shelf_optimizer.store_in_xlsx()