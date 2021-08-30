#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python3
"""
pulp used for solving linear programming
Please read WriteUp.pdf for more information
In the sudoku_solver we contained the input code for the AB.csv files
"""
import pulp


def variable_name(i, j, k):
  """
  It used to reture string "x_{i,j,k}back
  """

  return "x_{%d,%d,%d}" % (i, j, k)


def crange(a, b):
    """Reutrn range of [a,b]."""

    return range(a, b + 1)


class Sudoku:
    """
    In this Class we input the size of block of nxm, and the total size of N = m*n. 
    we used (i,j) to define the location of the number. So in the total grid of 9x9 Sudoku Quiz,
    (9,9) represent the number in the Right Down coner.
    please read WriteUp for more information
    """
    def __init__(self, m, n):
        """
        m: rows number per puzzle block.
        n: columns number per puzzle block.
        Use Self.m,n rather than using "m,n" is to return the value during the functions
        First we need to set up the rule of Sudoku to the LIP
        k standfor the value we solved or retured
        """

        self.m = m
        self.n = n

        N = m * n

        self.flag = False
        
        self.sudoku_model = pulp.LpProblem("Sudoku", pulp.LpMinimize)

        x_names = [variable_name(i, j, k)
                   for i in crange(1, N)
                   for j in crange(1, N)
                   for k in crange(1, N)]

        # setup dictionary with all variables x_{i,j,k}
        self.x = pulp.LpVariable.dict("%s",
                                      x_names,
                                      lowBound=0,
                                      upBound=1,
                                      cat=pulp.LpInteger)
        self.sudoku_model += 0

        # constraint: k appears only once in each i
        for i in crange(1, N):
            for k in crange(1, N):
                self.sudoku_model += sum([self.x[variable_name(i, j, k)]
                                          for j in crange(1, N)]) == 1

        # constraint: k appears only once in each j
        for j in crange(1, N):
            for k in crange(1, N):
                self.sudoku_model += sum([self.x[variable_name(i, j, k)]
                                          for i in crange(1, N)]) == 1

        # contraint: k appears only once in each block (I,J)
        for I in crange(1, n):
            for J in crange(1, m):

                i_low = (I - 1) * m + 1
                j_low = (J - 1) * n + 1
                block_i_values = range(i_low, i_low + m)
                block_j_values = range(j_low, j_low + n)

                for k in crange(1, N):
                    self.sudoku_model += sum([self.x[variable_name(i, j, k)]
                                              for i in block_i_values
                                              for j in block_j_values]) == 1

        # contraint: each cell (i,j) must have some value k
        for i in crange(1, N):
            for j in crange(1, N):
                self.sudoku_model += sum([self.x[variable_name(i, j, k)]
                                          for k in crange(1, N)]) == 1

    def set_cell_value(self, i, j, k):
        """
        Input cell(i,j) to get the value of ek
        """

        if self.sudoku_model.status != pulp.LpStatusNotSolved:
            self.flag = True
        self.sudoku_model += self.x[variable_name(i, j, k)] == 1

    def get_cell_value(self, i, j):
        """
        Returns the value of cell (i,j) or failed
        """

        N = self.size()

        for k in crange(1, N):
            if self.x[variable_name(i, j, k)].value() == 1:
                return k
        return None

    def solve(self):
        """
        Solves the puzzle and returns True if the puzzle is solved,
        False otherwise.
        """

        status = self.sudoku_model.solve()
        return status == pulp.LpStatusOptimal

    def size(self):
        """Returns N"""

        return self.m * self.n

