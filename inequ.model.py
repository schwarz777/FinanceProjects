# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 13:23:37 2019

@author: MichaelSchwarz
"""
import sys

class ind:
    """represents an individual with a certain wealth that can transact"""
    
    def __init__(self, initial_wealth):
        """Initializes the company."""
        self.wealth = [initial_wealth]


    def current_wealth(self):
        return self.wealth[len(self.wealth)-1]       
        
    def wealth_development(self): 
        print("the wealth of individual "+ str(id(self)) + " developpped:")
        print(self.wealth)
    
def transaction_game(ind1,ind2):
    """two individuals play a game. at stake is % of wealth of the poorer"""
    wealth_at_stake=min(ind1.current_wealth(),ind2.current_wealth())
    import random as r
    if r.random() > 0.5 : 
        print ("i1 wins")
        if ind1.current_wealth() < ind2.current_wealth():
            #ind1 is poorer and wins 20% of the stake    
            ind1.wealth.append(ind1.current_wealth() + wealth_at_stake*0.2)
            ind2.wealth.append(ind2.current_wealth() - wealth_at_stake*0.2) 
        else:
            #ind1 is richer and wins only 17% of the stake
            ind1.wealth.append(ind1.current_wealth() + wealth_at_stake*0.17) 
            ind2.wealth.append(ind2.current_wealth() - wealth_at_stake*0.17) 
      
    else: 
        print ("i2 wins")
        if ind1.current_wealth() < ind2.current_wealth():
            #ind1 is poorer and looses only 17% of its stake    
            ind2.wealth.append(ind2.current_wealth() + wealth_at_stake*0.17) 
            ind1.wealth.append(ind1.current_wealth() - wealth_at_stake*0.17) 
        else:
            #ind1 is richer and looses  20% of the stake
            ind2.wealth.append(ind2.current_wealth() + wealth_at_stake*0.2) 
            ind1.wealth.append(ind1.current_wealth() - wealth_at_stake*0.2) 
    
    print("game done and wealth moved")

#execute the transaction game   
#create individuals
list=[]
pop_size=3
i=0
while i < pop_size:
   list.append(ind(100))
   i+=1
print("initiated "+str(len(list))+" compnanies")
    
#execute transaction game
rounds=1000
rounds_played=0
import random as r
while rounds_played<rounds:
        players=r.sample(range(0,pop_size),2)
        print("game between"+str(players))
        transaction_game(list[players[0]],list[players[1]])
        rounds_played+=1
        for j in range(0,pop_size):
            print(list[j].current_wealth())
print("played " + str(rounds_played) + " rounds")
   
   

end_wealth=[]
for i in range(0,pop_size-1):
     end_wealth.append(list[i].current_wealth())

print(end_wealth)
max(end_wealth)


#pip install matplotlib
import matplotlib.pyplot as plt
import math as m
for i in range(0,pop_size):
    h=list[i].wealth
    plt.plot(range(0,len(h)),h)
plt.xlabel('t') 
plt.ylabel('wealth') 
plt.title('Wealth evolution of the different individuals') 
