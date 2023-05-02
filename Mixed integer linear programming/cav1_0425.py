# -*- coding: utf-8 -*-

import numpy as np
import gurobipy as gp
from gurobipy import GRB
from gurobipy import *

#define parameters
t=5
j=2
i=5
l=300
v_max=5
a_min=-2 #numercial
a_max=2
M=10**6
T=2
k1=3 #HDV safety following distance
k2=2 # CAV safety following distance
factor=100

#initial setting
#le = (1,4,10,15,19,23,29,34,36,50)
#ie = (1,2,3,4,5,1,2,3,4,5)
#iD = (2,1,3,2,1,3,1,2,3,2)
#ve = (3,3,5,1,4,3,1,2,2,5)
#k = (0,0,0,0,0,0,0,0,0,0)

#le = (1,5)
#ie = (1,5)
#iD = (3,4)
#ve = (5,5)
#k = (0,0)

le = (1,4)
ie = (1,1)
iD = (1,1)
ve = (5,1)
k = (1,0)

try:

    # Create a new model
    m = Model("mip1")
    
    # Create variables
    l_jt=m.addVars(j, t,lb=0, ub=l+t*v_max,vtype=GRB.INTEGER, name="l_jt")
    v_jt=m.addVars(j, t,lb=0, ub=v_max,vtype=GRB.INTEGER, name="v_jt")
    h_ljt=m.addVars(j, t,vtype=GRB.BINARY, name="h_ljt")
    h_rjt=m.addVars(j, t,vtype=GRB.BINARY, name="h_rjt")
    i_jt=m.addVars(j, t,lb=1, ub=i,vtype=GRB.INTEGER, name="i_jt")

    
    beta_jjt=m.addVars(j, j, t,vtype=GRB.BINARY, name="beta_jjt")
    beta1_jjt=m.addVars(j, j, t,vtype=GRB.BINARY, name="beta1_jjt")
    beta2_jjt=m.addVars(j, j, t,vtype=GRB.BINARY, name="beta2_jjt")
    
    sigma_jjt=m.addVars(j, j, t,vtype=GRB.BINARY, name="sigma_jjt")
    
    z_jjt=m.addVars(j, j, t,vtype=GRB.BINARY, name="z_jjt")
    
    d_j=m.addVars(j,vtype=GRB.INTEGER, name="d_j")
    d1_j=m.addVars(j,vtype=GRB.BINARY, name="d1_j")
    a_j=m.addVars(j,vtype=GRB.INTEGER, name="a_j")
    
#constraints

#trajectory definition
    for i0 in range(j):
        m.addConstr(l_jt[i0,0] == le[i0] + v_jt[i0,0]) #def1
        m.addConstr(i_jt[i0,0] == ie[i0] + h_ljt[i0,0] + h_rjt[i0,0]) #def2
        m.addConstr(v_jt[i0,0] - ve[i0] >= a_min) #bounds3
        m.addConstr(v_jt[i0,0] - ve[i0] <= a_max) #bounds3

#bounds
    for i1 in range(j):
        for t1 in range (t):
            m.addConstr(v_jt[i1,t1] >= 0) #bounds1
            m.addConstr(v_jt[i1,t1] <= v_max) #bounds1
            m.addConstr(h_ljt[i1,t1] + h_rjt[i1,t1] <= 1) #trajectory definition 5
            
    for i2 in range(j):
        for t2 in range (t-1):
            m.addConstr(v_jt[i2,t2+1] - v_jt[i2,t2] >= a_min) #bounds2
            m.addConstr(v_jt[i2,t2+1] - v_jt[i2,t2] <= a_max) #bounds2
            m.addConstr(i_jt[i2,t2+1] == i_jt[i2,t2] - h_ljt[i2,t2+1] + h_rjt[i2,t2+1]) #trajectory definition 4
            m.addConstr(l_jt[i2,t2+1] == l_jt[i2,t2] + v_jt[i2,t2+1]) #trajectory definition 3

    
# first j then j'
    for i5 in range(j):
        for i6 in range(j):
            for t4 in range(t):
                
#safety condition
                #beta group                
                m.addConstr(0.5 - (i_jt[i6,t4] - i_jt[i5,t4]) <= beta1_jjt[i5,i6,t4] * M)
                m.addConstr((i_jt[i6,t4] - i_jt[i5,t4]) - 0.5 <= (1 - beta1_jjt[i5,i6,t4]) * M)
                m.addConstr(0.5 - (i_jt[i5,t4] - i_jt[i6,t4]) <= (1 - beta2_jjt[i5,i6,t4]) * M)
                m.addConstr((i_jt[i5,t4] - i_jt[i6,t4]) - 0.5 <= beta2_jjt[i5,i6,t4] * M)
                m.addConstr(beta_jjt[i5,i6,t4] == beta1_jjt[i5,i6,t4] - beta2_jjt[i5,i6,t4])
                
                #sigma group
                m.addConstr(0.5 - (l_jt[i6,t4] - l_jt[i5,t4]) <= (1 - sigma_jjt[i5,i6,t4]) * M)
                m.addConstr((l_jt[i6,t4] - l_jt[i5,t4]) - 0.5 <= sigma_jjt[i5,i6,t4] * M)
                
                #zeta group
                m.addConstr(2 * z_jjt[i5,i6,t4] <= beta_jjt[i5,i6,t4] + sigma_jjt[i5,i6,t4])
                m.addConstr(2 * z_jjt[i5,i6,t4] >= beta_jjt[i5,i6,t4] + sigma_jjt[i5,i6,t4] - 1)
                
                #direct safety condition
                m.addConstr(l_jt[i6,t4] - l_jt[i5,t4] >= z_jjt[i5,i6,t4] * (k2*k[i5] + k1*(1-k[i5])) )

# constraints from objective function
    for i9 in range(j):
        m.addConstr(0.5 - (l - l_jt[i9,T-1]) <= M * (1 - d1_j[i9]))
        m.addConstr((l - l_jt[i9,T-1]) - 0.5 <= M * d1_j[i9])
        m.addConstr(d_j[i9] <= M * d1_j[i9])
        m.addConstr(d_j[i9] >= -M * d1_j[i9])
        m.addConstr(d_j[i9] <= l - l_jt[i9,T-1] + M * (1 - d1_j[i9]))
        m.addConstr(d_j[i9] >= l - l_jt[i9,T-1] - M * (1 - d1_j[i9]))
        m.addConstr(a_j[i9] >= iD[i9] - i_jt[i9,T-1])
        m.addConstr(a_j[i9] >= i_jt[i9,T-1] - iD[i9])


    m.setObjective( a_j.sum('*') + d_j.sum('*'), GRB.MINIMIZE)

    m.optimize()
    
    f = open("result_crowded2.txt", "a")
    for v in m.getVars():
        print('%s %g' % (v.varName, v.x), file=f)

    print('Obj: %g' % m.objVal)
    f.close()

except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')    