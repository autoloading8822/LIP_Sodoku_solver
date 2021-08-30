#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy
import random
import pandas as pd
import scipy.sparse as scs
import os
random.seed()
file_name = input("name.csv")
data = pd.read_csv(file_name)
datalen = len(data)
print('data set legnth:', len(data))
# enumerate the data strings in quizzes
print(data["quizzes"][0:datalen])
# enumerate the corresponding solution strings.
print(data["solutions"][0:datalen])
# Take a close look at one string in quizzes  
quiz = data["quizzes"][0]
solution = data["solutions"][0]
#print(quiz, '\ndata type is:', type(quiz))
# we can turn it into a numpy array by the following
quizMatrix = numpy.reshape([int(c) for c in quiz], (9,9))
solutionMatrix = numpy.reshape([int(c) for c in solution], (9,9))
global successN
successN = 0
NumDigits = 9  # Number of digits standard Sudoku puzzles should be 9).


class Population(object):
    """Population is a collection of candidates or chromosomes. These are basically the possible solutions for the particular sudoku problem"""

    def __init__(self):
        self.chromosomes = []
        return

    def seed(self, Nc, given):
        self.chromosomes = []
        # Determining the possible values that each square can take
        helper = Candidate()
        helper.values = [[[] for j in range(0, NumDigits)] for i in range(0, NumDigits)]
        for row in range(0, NumDigits):
            for column in range(0, NumDigits):
                for value in range(1, 10):
                    if((given.values[row][column] == 0) and not (given.isColumnDuplicate(column, value) or given.isBlockDuplicate(row, column, value) or given.isRowDuplicate(row, value))):
                        # Value is available.
                        helper.values[row][column].append(value)
                    elif(given.values[row][column] != 0):
                        # Given/known value from file.
                        helper.values[row][column].append(given.values[row][column])
                        break

        # Seeding  a new population.       
        for p in range(0, Nc):
            g = Candidate()
            for i in range(0, NumDigits): # New row in candidate.
                row = numpy.zeros(NumDigits, dtype=int)
                
                # Fill in the givens.
                for j in range(0, NumDigits): # New column j value in row i.
                
                    # If value is already given, don't change it.
                    if(given.values[i][j] != 0):
                        row[j] = given.values[i][j]
                    # Fill in the gaps using the helper board.
                    elif(given.values[i][j] == 0):
                        row[j] = helper.values[i][j][random.randint(0, len(helper.values[i][j])-1)]

                # If we don't have a valid board, then try again. There must be no duplicates in the row.
                while(len(list(set(row))) != NumDigits):
                    for j in range(0, NumDigits):
                        if(given.values[i][j] == 0):
                            row[j] = helper.values[i][j][random.randint(0, len(helper.values[i][j])-1)]

                g.values[i] = row

            self.chromosomes.append(g)
        
        # Compute the fitness of all candidates in the population.
        self.updateFitness()
        print("Seeding complete.")
        return
        
    def updateFitness(self):
        """ Update fitness of every candidate/chromosome. """
        for chromosomes in self.chromosomes:
            chromosomes.updateFitness()
        return
        
    def sort(self):
        """ Sort the population based on fitness. """
        for i in range(len(self.chromosomes)-1):
            max = i
            for j in range(i+1, len(self.chromosomes)):
                if self.chromosomes[max].fitness < self.chromosomes[j].fitness:
                    max = j
            temp = self.chromosomes[i]
            self.chromosomes[i] = self.chromosomes[max]
            self.chromosomes[max] = temp
        return

class Candidate(object):
    """ A candidate solutions to the Sudoku puzzle. """
    def __init__(self):
        self.values = numpy.zeros((NumDigits, NumDigits), dtype=int)
        self.fitness = None
        return

    def updateFitness(self):
        """ The fitness of a candidate solution is determined by how close it is to being the actual solution to the puzzle. The actual solution (i.e. the 'fittest') is defined as a 9x9 grid of numbers in the range [1, 9] where each row, column and 3x3 block contains the numbers [1, 9] without any duplicates (see e.g. http://www.sudoku.com/); if there are any duplicates then the fitness will be lower. """
        
        columnCount = numpy.zeros(NumDigits, dtype=int)
        Noblock = numpy.zeros(NumDigits, dtype=int)
        coumnSum = 0
        blockSum = 0

        for i in range(0, NumDigits):  # For each column...
            nonzeronum = 0
            for j in range(0, NumDigits):  # For each number within the current column...
                columnCount[self.values[j][i]-1] += 1  # ...Update list with occurrence of a particular number.

            #coumnSum = coumnSum + (1/len(set(columnCount)))/NumDigits
            
            for k in range(0, NumDigits):
                if columnCount[k]!=0:
                    nonzeronum += 1
            nonzeronum = nonzeronum/NumDigits
            coumnSum = (coumnSum + nonzeronum)
            columnCount = numpy.zeros(NumDigits, dtype=int)
        coumnSum = coumnSum/NumDigits

        # For each block...
        for i in range(0, NumDigits, 3):
            for j in range(0, NumDigits, 3):
                Noblock[self.values[i][j]-1] += 1
                Noblock[self.values[i][j+1]-1] += 1
                Noblock[self.values[i][j+2]-1] += 1
                
                Noblock[self.values[i+1][j]-1] += 1
                Noblock[self.values[i+1][j+1]-1] += 1
                Noblock[self.values[i+1][j+2]-1] += 1
                
                Noblock[self.values[i+2][j]-1] += 1
                Noblock[self.values[i+2][j+1]-1] += 1
                Noblock[self.values[i+2][j+2]-1] += 1

                #blockSum = blockSum + (1/len(set(Noblock)))/NumDigits
                #Noblock = numpy.zeros(NumDigits, dtype=int)
                nonzeronum = 0
                for k in range(0, NumDigits):
                    if Noblock[k]!=0:
                        nonzeronum += 1
                nonzeronum = nonzeronum/NumDigits
                blockSum = blockSum + nonzeronum
                Noblock = numpy.zeros(NumDigits, dtype=int)
        blockSum = blockSum/NumDigits



        if (int(coumnSum) == 1 and int(blockSum) == 1):
            fitness = 1.0
        else:
            fitness = coumnSum * blockSum
        
        self.fitness = fitness
        return
        
    def mutate(self, mutationRate, given):
        """ Mutate a candidate by picking a row, and then picking two values within that row to swap. """

        r = random.uniform(0, 1.1)
        while(r > 1): # Outside [0, 1] boundary - choose another
            r = random.uniform(0, 1.1)
    
        success = False
        if (r < mutationRate):  # Mutate.
            while(not success):
                row1 = random.randint(0, 8)
                row2 = random.randint(0, 8)
                row2 = row1
                
                fromColumn = random.randint(0, 8)
                toColumn = random.randint(0, 8)
                while(fromColumn == toColumn):
                    fromColumn = random.randint(0, 8)
                    toColumn = random.randint(0, 8)   

                # Check if the two places are free...
                if(given.values[row1][fromColumn] == 0 and given.values[row1][toColumn] == 0):
                    # ...and that we are not causing a duplicate in the rows' columns.
                    if(not given.isColumnDuplicate(toColumn, self.values[row1][fromColumn])
                       and not given.isColumnDuplicate(fromColumn, self.values[row2][toColumn])
                       and not given.isBlockDuplicate(row2, toColumn, self.values[row1][fromColumn])
                       and not given.isBlockDuplicate(row1, fromColumn, self.values[row2][toColumn])):
                    
                        # Swap values.
                        temp = self.values[row2][toColumn]
                        self.values[row2][toColumn] = self.values[row1][fromColumn]
                        self.values[row1][fromColumn] = temp
                        success = True
    
        return success


class Given(Candidate):
    """ The grid containing the given/known values. """

    def __init__(self, values):
        self.values = values
        return
        
    def isRowDuplicate(self, row, value):
        """ Check whether there is a duplicate of a fixed/given value in a row. """
        for column in range(0, NumDigits):
            if(self.values[row][column] == value):
               return True
        return False

    def isColumnDuplicate(self, column, value):
        """ Check whether there is a duplicate of a fixed/given value in a column. """
        for row in range(0, NumDigits):
            if(self.values[row][column] == value):
               return True
        return False

    def isBlockDuplicate(self, row, column, value):
        """ Check whether there is a duplicate of a fixed/given value in a 3 x 3 block. """
        i = 3*(int(row/3))
        j = 3*(int(column/3))

        if((self.values[i][j] == value)
           or (self.values[i][j+1] == value)
           or (self.values[i][j+2] == value)
           or (self.values[i+1][j] == value)
           or (self.values[i+1][j+1] == value)
           or (self.values[i+1][j+2] == value)
           or (self.values[i+2][j] == value)
           or (self.values[i+2][j+1] == value)
           or (self.values[i+2][j+2] == value)):
            return True
        else:
            return False


class Tournament(object):
    """ The crossover function requires two parents to be selected from the population pool. The Tournament class is used to do this.
    
    Two individuals are selected from the population pool and a random number in [0, 1] is chosen. If this number is less than the 'selection rate' (e.g. 0.85), then the fitter individual is selected; otherwise, the weaker one is selected.
    """

    def __init__(self):
        return
        
    def compete(self, chromosomes):
        """ Pick 2 random candidates from the population and get them to compete against each other. """
        c1 = chromosomes[random.randint(0, len(chromosomes)-1)]
        c2 = chromosomes[random.randint(0, len(chromosomes)-1)]
        f1 = c1.fitness
        f2 = c2.fitness

        # Find the fittest and the weakest.
        if(f1 > f2):
            fittest = c1
            weakest = c2
        else:
            fittest = c2
            weakest = c1

        selection_rate = 0.85
        r = random.uniform(0, 1.1)
        while(r > 1):  # Outside [0, 1] boundary. Choose another.
            r = random.uniform(0, 1.1)
        if(r < selection_rate):
            return fittest
        else:
            return weakest
    
class CycleCrossover(object):
    """ Crossover relates to the analogy of genes within each parent candidate mixing together in the hopes of creating a fitter child candidate. Cycle crossover is used here (see e.g. A. E. Eiben, J. E. Smith. Introduction to Evolutionary Computing. Springer, 2007). """

    def __init__(self):
        return
    
    def crossover(self, parent1, parent2, crossoverRate):
        """ Create two new child candidates by crossing over parent genes. """
        child1 = Candidate()
        child2 = Candidate()
        
        # Make a copy of the parent genes.
        child1.values = numpy.copy(parent1.values)
        child1.fitness = parent1.fitness
        child2.values = numpy.copy(parent2.values)
        child2.fitness = parent2.fitness
        
        r = random.uniform(0, 1.1)
        while(r > 1):  # Outside [0, 1] boundary. Choose another.
            r = random.uniform(0, 1.1)
            
        # Perform crossover.
        if (r < crossoverRate):
            # Pick a crossover point. Crossover must have at least 1 row (and at most Nd-1) rows.
            crossoverPoint1 = random.randint(0, 8)
            crossoverPoint2 = random.randint(1, 9)
            while(crossoverPoint1 == crossoverPoint2):
                crossoverPoint1 = random.randint(0, 8)
                crossoverPoint2 = random.randint(1, 9)
                
            if(crossoverPoint1 > crossoverPoint2):
                temp = crossoverPoint1
                crossoverPoint1 = crossoverPoint2
                crossoverPoint2 = temp
                
            for i in range(crossoverPoint1, crossoverPoint2):
                child1.values[i], child2.values[i] = self.crossoverRows(child1.values[i], child2.values[i])

        return child1, child2

    def crossoverRows(self, row1, row2): 
        childRow1 = numpy.zeros(NumDigits)
        childRow2 = numpy.zeros(NumDigits)

        remaining = [i for i in range(1, NumDigits+1)]
        cycle = 0
        
        while((0 in childRow1) and (0 in childRow2)):  # While child rows not complete...
            if(cycle % 2 == 0):  # Even cycles.
                # Assign next unused value.
                index = self.findUnused(row1, remaining)
                start = row1[index]
                remaining.remove(row1[index])
                childRow1[index] = row1[index]
                childRow2[index] = row2[index]
                next = row2[index]
                
                while(next != start):  # While cycle not done...
                    index = self.findValue(row1, next)
                    childRow1[index] = row1[index]
                    remaining.remove(row1[index])
                    childRow2[index] = row2[index]
                    next = row2[index]

                cycle += 1

            else:  # Odd cycle - flip values.
                index = self.findUnused(row1, remaining)
                start = row1[index]
                remaining.remove(row1[index])
                childRow1[index] = row2[index]
                childRow2[index] = row1[index]
                next = row2[index]
                
                while(next != start):  # While cycle not done...
                    index = self.findValue(row1, next)
                    childRow1[index] = row2[index]
                    remaining.remove(row1[index])
                    childRow2[index] = row1[index]
                    next = row2[index]
                    
                cycle += 1
            
        return childRow1, childRow2  
           
    def findUnused(self, parent_row, remaining):
        for i in range(0, len(parent_row)):
            if(parent_row[i] in remaining):
                return i

    def findValue(self, parent_row, value):
        for i in range(0, len(parent_row)):
            if(parent_row[i] == value):
                return i


class Sudoku(object):
    
    def __init__(self):
        self.given = None
        return
    
    def load(self, path):
        # Load a file containing SUDOKU to solve.
        with open(path, "r") as f:  
            values = quizMatrix
            self.given = Given(values)
            print("INPUT\n", values)
        return
    

    def save(self, path, solution):
        # Save a configuration to a file.
        with open(path, "w") as f:
            numpy.savetxt(f, solution.values.reshape(NumDigits*NumDigits), fmt='%d')
        return
        
    def solve(self):
        global successN
        Nc = 200  #Number of candidates OR chromosomes(i.e. population size).
        Ne = int(0.6*Nc)  # Number of elites = 120
        Ng = 1500 # Number of generations.
        Nm = 0  # to count Number of mutations.
        staleCount = 0 #count number of times generation is staling
        prevFitness = 0

        # Defining variables used to update the mutationRate
        phi = 0 #to count number of times when child is better than parent
        sigma = 1 #used for updating mutation rate
        mutationRate = 0.5
    
        # Generating initial population OR Seeding.
        self.population = Population()
        self.population.seed(Nc, self.given)
    
        # For up to 1000 generations...
        for generation in range(0, Ng):
            print("Generation %d" % generation)
            
            # Check for a solution.
            bestFitness = 0.0
            bestSolution = self.given
            #for each generation, traverse all the candidates or chromosomes to check for solution
            for c in range(0, Nc):
                fitness = self.population.chromosomes[c].fitness
                if(int(fitness) == 1):
                    print("Solution found at generation %d!" % generation)
                    print(self.population.chromosomes[c].values)
                    print("Key Solution is:\n",solutionMatrix)
                    successN = successN +1
                    print("We have test", x,"quiz, which we have",successN, "succeed" )
                    successR = successN/datalen
                    print("Success Rate is",successR)
                    return self.population.chromosomes[c]

                # Find the best fitness.
                if(fitness > bestFitness):
                    bestFitness = fitness
                    bestSolution = self.population.chromosomes[c].values

            print("Best fitness: %f" % bestFitness)

            # Create the next population.
            nextPopulation = []

            # Select elites (the fittest candidates) and preserve them for the next generation.
            #0.6*200=120 elites in new generation
            self.population.sort()
            elites = []
            for e in range(0, Ne):
                elite = Candidate()
                elite.values = numpy.copy(self.population.chromosomes[e].values)
                elites.append(elite)

            # Create the rest of the candidates. 80 children, so run loop 40 times
            for count in range(Ne, Nc, 2):
                # Select parents from population via a tournament.
                t = Tournament()
                parent1 = t.compete(self.population.chromosomes)
                parent2 = t.compete(self.population.chromosomes)
                
                ## Cross-over.
                cc = CycleCrossover()
                child1, child2 = cc.crossover(parent1, parent2, crossoverRate=1.0)
                
                # Mutate child1.
                child1.updateFitness()
                oldFitness = child1.fitness
                success = child1.mutate(mutationRate, self.given)
                child1.updateFitness()
                if(success):
                    Nm += 1
                    if(child1.fitness > oldFitness):  # Used to calculate the relative success rate of mutations.
                        phi = phi + 1
                
                # Mutate child2.
                child2.updateFitness()
                oldFitness = child2.fitness
                success = child2.mutate(mutationRate, self.given)
                child2.updateFitness()
                if(success):
                    Nm += 1
                    if(child2.fitness > oldFitness):  # Used to calculate the relative success rate of mutations.
                        phi = phi + 1
                
                # Add children to new population.
                nextPopulation.append(child1)
                nextPopulation.append(child2)

            # Append elites onto the end of the population. These will not have been affected by crossover or mutation.
            for e in range(0, Ne):
                nextPopulation.append(elites[e])
                
            # Select next generation.
            self.population.chromosomes = nextPopulation
            self.population.updateFitness()
            
            # Calculate new adaptive mutation rate (based on Rechenberg's 1/5 success rule). This is to stop too much mutation as the fitness progresses towards unity.
            if(Nm == 0):
                phi = 0  # Avoid divide by zero.
            else:
                phi = phi / Nm
            
            if(phi > 0.2):
                sigma = sigma*0.998    #sigma decreases, less mutationRate
            if(phi < 0.2):
                sigma = sigma/0.998    #sigma increases, more mutationRate
                

            mutationRate = abs(numpy.random.normal(loc=0.0, scale=sigma, size=None))
            while mutationRate>1:
                mutationRate = abs(numpy.random.normal(loc=0.0, scale=sigma, size=None))
        
            # Check for stale population.
            self.population.sort()

            if generation==0:
                prevFitness = bestFitness
                staleCount = 1

            elif prevFitness == bestFitness:
                    staleCount += 1

            elif prevFitness!=bestFitness:
                staleCount = 0
                prevFitness = bestFitness

            # Re-seed the population if 100 generations have passed with the fittest two candidates always having the same fitness.
            if(staleCount >= 100):
                print("The population has gone stale. Re-seeding...")
                self.population.seed(Nc, self.given)
                staleCount = 0
                sigma = 1
                phi = 0
                mutations = 0
                mutationRate = 0.5
        
        print("Fail to find the solution and the best solution we can find is:\n", bestSolution)
        print("Key Solution is:\n",solutionMatrix)
        return None


for x in range (1,datalen):
    quiz = data["quizzes"][x]
    solution = data["solutions"][x]
    quizMatrix = numpy.reshape([int(c) for c in quiz], (9,9))
    solutionMatrix = numpy.reshape([int(c) for c in solution], (9,9))
    s = Sudoku()
    s.load("small1.csv")
    solution = s.solve()
    #if(solution):
        #s.save("solution.txt", solution)
    

