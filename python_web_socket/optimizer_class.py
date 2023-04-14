#create class for pulp libery
from array import array
from typing import overload
import pulp
import numpy as np
import pandas as pd
import datetime

class pulp_solver:
    
    def __init__(self,type_problem):
        self.problem = pulp.LpProblem(type_problem)
        self.dict_variable = {}
    
    def create_variable(self,name:str,indexes:np.array,low:int,category:str):
        select_category = {
            "integer": pulp.LpInteger,
            "binary": pulp.LpBinary,
            "continuous": pulp.LpContinuous
        }
        self.dict_variable[name] = np.array(pulp.LpVariable.matrix(name, indexs=indexes,lowBound=low, cat=select_category.get(category, None)))

    

    def create_constraint_by_name_array(self,name_value_1:str,constant_value_1:float,array_value: np.array,constant_value_2:float,operators:str,condition:np.array):
        self.make_constraint(
                constant_value_1*self.dict_variable.get(name_value_1, None),
                constant_value_2*array_value,
                operators,
                condition
            )

    def create_constraint_by_name_array_with_condition(self,name_value_1:str,constant_value_1:float,array_value: np.array,constant_value_2:float,operators:str,condition:np.array):
        self.make_constraint(
                constant_value_1*self.dict_variable.get(name_value_1, None),
                constant_value_2*array_value,
                operators,
                condition
            )
    def create_constraint_by_name_name(self,name_value_1:str,constant_value_1:float,name_value_2:str,constant_value_2:float,operators:str,condition:np.array):
        self.make_constraint(
                constant_value_1*self.dict_variable.get(name_value_1, None),
                constant_value_2*self.dict_variable.get(name_value_2, None),
                operators,
                condition
            )

    def make_constraint(self,array_value_1:np.array,array_value_2:np.array,operators:str,condition):
        for i in condition:
            switcher = {
                "<=": array_value_1[i] <= array_value_2[i],
                ">=": array_value_1[i] >= array_value_2[i],
                "==": array_value_1[i] == array_value_2[i],
            }
            self.problem += switcher.get(operators,None)


    def create_objetive_function(self,*kwargs):
        concatenate_values = np.array([])
        coefficients_values = np.array([])
        dicts = {
            "lot_size":1,
            "deficit": 1,
            "excess": 1
        }
        for x in kwargs:
            concatenate_values = np.concatenate((concatenate_values,self.dict_variable.get(x, None)), axis=None)
            coefficients_values = np.concatenate((coefficients_values,np.repeat(dicts.get(x,1),len(self.dict_variable.get(x, None)))), axis=None)
        sum = np.dot(coefficients_values, concatenate_values)
        self.problem += sum

    def get_variable_by_name(self,name):
        return self.dict_variable.get(name, None)
    def view_problem(self):
        print(self.problem)

    def solve_problem(self):
        self.problem.solve()
    
    def get_solution(self):
        return self.problem.status
    