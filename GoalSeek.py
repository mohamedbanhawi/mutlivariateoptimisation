from scipy.optimize import fmin_slsqp
import numpy as np
import csv
#to do list ! ratios
 
print '##reading data###'
with open("/Users/mohamedbanhawi/Desktop/NutritientList-masterunit.csv") as f:
    lines=[line.split(',') for line in f]   

print len(lines)
     
###read from csv### 
n_ingredients = len(lines) - 7 # ingredients start at the eight column
n_components = len(lines[0])-5 # components start at the fifth column

##input target spec
components_min = map(float,lines[1][5:])
components_max = map(float,lines[2][5:])
components_target = map(float,lines[3][5:])

#print components_min, components_max

## % of component in ingredient (composition)
c=[]
ingredients_name = []
ingredients_min = []
ingredients_max = []
intitial_ingredients = []
for i in range(n_ingredients):
       
       c.append(map(float,lines[7+i][5:]))
       #print lines[7+i][3]
       ingredients_min.append(float(lines[7+i][3])/100.0)
       ingredients_max.append(float(lines[7+i][4])/100.0)
       intitial_ingredients.append(float(lines[7+i][2])/100.0)
       ingredients_name.append((lines[7+i][0]))

#create constraint tuples 
ingredients_bounds = zip(ingredients_min,ingredients_max)
ingredients_bounds = tuple(map(tuple,ingredients_bounds))

print ingredients_bounds
print intitial_ingredients

#setup 
constraints = []

#define function for ingredient constraint
def const_min(i):
		return lambda x: x[i]-ingredients_min[i]
	
#define function for ingredient constraint
def const_max(i):
		return lambda x: -x[i]+ingredients_max[i]
		

def coeff_min(i,j):
		return lambda x: -components_min[j]+x[i]*c[j][i]
		
def coeff_max(i,j):
		return lambda x: components_min[j]-x[i]*c[j][i]	
		
#objective to set weight to one hundred
 
def objective(ingredient):
    obj = -1.0;
    for i in range(n_ingredients):
        obj = obj + ingredient [i]
    return obj**2

##-depreciated - replaced with bounds in SLSQP	 
##define equality range limit constraints
#for i in range(n_ingredients):
#	if ingredients_max[i]>0:
#		constraints.append(const_max(i))
#	if ingredients_min[i]>=0:
#		constraints.append(const_min(i))
		
#	#if intitial_ingredients[i]==0:
#	intitial_ingredients.append(1.0/n_ingredients)
##print intitial_ingredients

#define formulas for parameter
for j in range (n_components):
	fmin= lambda x: 0
	fmax= lambda x: 0
	for i in range (n_ingredients):
		fmin = lambda x, fmin=fmin, j=j,i=i: x[i]*c[i][j] + fmin(x)
		fmax = lambda x, fmax=fmax, j=j,i=i: x[i]*c[i][j] + fmax(x)
	fmin = lambda x,j=j, fmin=fmin: fmin(x) - components_min[j]
	fmax = lambda x,j=j, fmax=fmax: -fmax(x) + components_max[j]
	constraints.append(fmin)
	if components_max[j] > 0:
		constraints.append(fmax)
	if components_target[j]>0:	
		fmin = lambda x,j=j, fmin=fmin: fmin(x)+components_min[j]-components_target[j]
		fmax = lambda x,j=j, fmax=fmax: -fmax(x) - components_max[j]+components_target[j]
		constraints.append(fmin)
		constraints.append(fmax)


print '##starting slsqp optimisation###'
 
res = fmin_slsqp(objective, intitial_ingredients , ieqcons= constraints, bounds = ingredients_bounds)

res = res*100.0

print '##optimisation complete###'

#output to csv
with open('/Users/mohamedbanhawi/Desktop/Results.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    spamwriter.writerow(['Ingredients','% of Recipe'])
    for i in range(len(res)):
    	spamwriter.writerow([ingredients_name[i],res[i]])
    
