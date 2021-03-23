#! /usr/bin/env python

# imports of external packages to use in our code
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from collections import Counter

# gets rules from the text file associated with input files
def GetRules(InputFile):
    RulesFile = "rules_" + InputFile
    rules = []
    with open(RulesFile, "r") as rulesfile:
        for rule in rulesfile:
            rules.append(int(rule))
        # print("Ncards: " + str(rules[0]))
        # print("Ngames: " + str(rules[1]))
        # print("Nsets: " + str(rules[2]))
        # print("gimme: " + str(rules[3]))
    return rules

# Reorganizes inputfile data for our use, outputs as tuple
def DataResults(InputFile):
    with open(InputFile,'r') as sets:
        # organizes data into tuple where each item is a set
        # removes information that is not a digit
        data = [[int(x) for x in line.split(',') if x.isdigit()] for line in sets]
        return data
    
# just gets all of the values from the tuple and compiles it
def TotalResults(DataResults):
    results = []
    for data in DataResults:
        for x in data:
            results.append(x)
    return results

# gets probabilities of data based on size of hand for density plot
def GetProbability(List1,Size):
    x = np.linspace(0,Size,Size+1)
    y = []
    p_y = []
    countdict = Counter(List1)
    counts = countdict.items()
    counts = sorted(counts)
    i,j = zip(*counts)
    for x_i in x:
        if x_i not in i:
            y.append(0)
        if x_i in i:
            y_i = i.index(x_i)
            y.append(j[y_i])
    Y = sum(y)
    for y_i in y:
        y_i = y_i/Y
        p_y.append(y_i)
    return x,p_y

# Gives Likelihood for single set
def GetLikelihood(xlist, Prob0, Prob1):
    # Likelihood as if this were null
    p0list = []
    p1list = []
    Prob0x = list(Prob0[0])
    Prob0y = list(Prob0[1])
    Prob1x = list(Prob1[0])
    Prob1y = list(Prob1[1])
    for x in xlist:
        if x in Prob0x:
            y_iy = Prob0x.index(x)
            p0list.append(Prob0y[y_iy])
        else: p0list.append(0)
        if x in Prob1x:
            y_ix = Prob1x.index(x)
            p1list.append(Prob1y[y_ix])
        else: p1list.append(0)
    P_0 = np.product(p0list)
    P_1 = np.product(p1list)
    L = np.log(P_0/P_1)
    return L

def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

# main function for our coin toss Python code
if __name__ == "__main__":
    # not making any assumptions about what is provided by user
    haveH0 = False
    haveH1 = False
    
    # default gimme
    gimme = 0
    
    # default number of cards, set to match default from CardgameSim
    Ncards = 20
    
    # default confidence interval
    confidence = .95
    
    # available options for user input
    if '-input0' in sys.argv:
        p = sys.argv.index('-input0')
        InputFile0 = sys.argv[p+1]
        haveH0 = True
    if '-input1' in sys.argv:
        p = sys.argv.index('-input1')
        InputFile1 = sys.argv[p+1]
        haveH1 = True
    if '-conf' in sys.argv:
        p = sys.argv.index('-conf')
        cn = float(sys.argv[p+1])
        if cn > 0 and cn < 1:
            confidence = cn
    # if the user includes the flag -h or --help print the options
    if '-h' in sys.argv or '--help' in sys.argv or not haveH0:
        print ("Usage: %s [options]" % sys.argv[0])
        print ("  options:")
        print ("   --help(-h)          print options")
        print ("   -input0 [filename]  name of file for H0 data")
        print ("   -input1 [filename]  name of file for H1 data")
        print ("   -conf [number]      confidence level between 0 and 1")
        sys.exit(1)
    
    # get data from the input file rules so we know what we are working with
    rules0 = GetRules(InputFile0)
    Ncards0 = rules0[0]
    Ngames0 = rules0[1]
    Nsets0 = rules0[2]
    gimme0 = rules0[3]
    
    rules1 = GetRules(InputFile1)
    Ncards1 = rules1[0]
    Ngames1 = rules1[1]
    Nsets1 = rules1[2]
    gimme1 = rules1[3]
    
    # gives ratio of games that will definitely win when cheated
    willwin0 = gimme0/(Ncards0//2)
    willwin1 = gimme1/(Ncards1//2)
    
    # gets probability of winning each round from number of cheater cards
    p0 = round(1*willwin0 + .5*(1-willwin0),3)
    p1 = round(1*willwin1 + .5*(1-willwin1),3)
    
    # use our definitions to get data
    data0 = DataResults(InputFile0)
    data1 = DataResults(InputFile1)
    
    Outcome0 = TotalResults(data0)
    Outcome1 = TotalResults(data1)
    
    Prob0 = GetProbability(Outcome0,Ncards//2)
    Prob1 = GetProbability(Outcome1,Ncards//2)
    
    # iterate LLR for all null hypothesis sets, return as list for plotting
    L_X = []
    for data0_i in data0:
        l_x = GetLikelihood(data0_i, Prob1, Prob0)
        L_X.append(l_x)
    L_X = [v for v in L_X if not math.isinf(v)]
        
    # iterate LLR for all alternative hypothesis sets, return as list for plotting
    L_Y = []
    for data1_i in data1:
        l_y = GetLikelihood(data1_i, Prob1, Prob0)
        L_Y.append(l_y)
    L_Y = [v for v in L_Y if not math.isinf(v) and not math.isnan(v)]
    
    # combine data to look at max and min for plotting
    L_XY = L_X + L_Y
            
    # Gets max and min of data. Also determines optimal bin width for plotting
    Outcome0max = max(Outcome0)
    Outcome0min = min(Outcome0)
    binwidth0 = int(Outcome0max) - int(Outcome0min)
    
    Outcome1max = max(Outcome1)
    Outcome1min = min(Outcome1)
    binwidth1 = int(Outcome1max) - int(Outcome1min)
    
    binwidth = 1
    
    # at this point we choose to reject H_0 in favor of H_1
    alpha = round(1-confidence,2)
    
    # sort original L_X
    L_X.sort()
    # xnorm = x-xmin/(xmax-xmin)
    # normalize data
    Xnorm = NormalizeData(L_X)
    # find x just before "confidence" and get index
    critval_index = np.argwhere(np.array(Xnorm)>confidence).tolist()[0][0]
    # plot vertical line at this critval in indexed location of L_X
    critval = round(L_X[critval_index],3)
    
    # take x value of alpha
    # get index for where critval <= L_Y (L_Y exeeds critval)
    L_Y.sort()
    Ynorm = NormalizeData(L_Y)
    # get index value from critval and record as "beta"
    beta_index = np.argwhere(np.array(L_Y)>critval).tolist()[0][0]
    beta = round(Ynorm[beta_index],3)
    power = 1 - beta
                    
# # Frequency plot
#     title1 = "Frequency Table for Number of Games Won"
                
#     # make figure
#     plt.figure()
#     plt.hist(Outcome0, binwidth0, facecolor='deepskyblue',
#               alpha=0.5, align = 'left', label="$\\mathbb{H}_0$")
#     if haveH1: 
#         plt.hist(Outcome1, binwidth1, facecolor='salmon',
#                   alpha=0.7, align = 'left', label="$\\mathbb{H}_1$")
    
#     # Plot a line to indicate that games were not played with similar card numbers
#     if Ncards0 != Ncards1:
#         plt.axvline(min(Ncards0,Ncards1)/2-.5, color = 'black', 
#                     label = 'Upper limit for fewer cards', linestyle = '--')
      
#     plt.xlabel('$N_{wins}$ per game')
#     plt.ylabel('Frequency')
#     plt.legend(loc = 2)
#     plt.xlim(-.5 , max(Ncards0,Ncards1)/2+.5)
#     plt.tick_params(axis='both')
#     plt.title(title1)
#     plt.grid(True)

#     plt.show()
    
# # Density plot
#     title2 = "Density Table for Number of Games Won"
                
#     # make figure
#     plt.figure()
#     plt.bar(Prob0[0], Prob0[1], width=1, facecolor='deepskyblue',
#               alpha=0.5, label="$\\mathbb{H}_0$")
#     plt.bar(Prob1[0], Prob1[1], width=1, facecolor='salmon',
#               alpha=0.5, label="$\\mathbb{H}_1$")
    
#     # Plot a line to indicate that games were not played with similar card numbers
#     if Ncards0 != Ncards1:
#         plt.axvline(min(Ncards0,Ncards1)/2-.5, color = 'black', 
#                     label = 'Upper limit for fewer cards', linestyle = '--')
      
#     plt.xlabel('$N_{wins}$ per game')
#     plt.ylabel('Probability')
#     plt.legend(loc = 2)
#     plt.xlim(-.5 , max(Ncards0,Ncards1)/2+.5)
#     plt.tick_params(axis='both')
#     plt.title(title2)
#     plt.grid(True)

#     plt.show()

# # Likelihood plot
#     title3 = str(Nsets0) + " sets with " + str(Ngames0) + " games / set and " + str(Ncards0) + " cards per game\n$\\alpha = $" + str(alpha) + "; $\\beta = $" + str(beta)
                
#     # make figure data, bins=np.arange(min(data), max(data) + binwidth, binwidth)
#     plt.figure()
#     plt.hist(L_X, bins=np.arange(min(L_XY), max(L_XY) + binwidth, binwidth),
#               facecolor='deepskyblue', density = True, alpha=0.5, align = 'left',
#               label="assuming $\\mathbb{H}_0$")
#     plt.hist(L_Y, bins=np.arange(min(L_XY), max(L_XY) + binwidth, binwidth),
#               facecolor='salmon', density = True, alpha=0.5, align = 'left',
#               label="assuming $\\mathbb{H}_1$")
    
#     plt.axvline(critval, color = 'black', linewidth = 1)
#                      # label = "$\\alpha = $" + str(alpha) + "\n$\\beta = $" + str(beta))
#     plt.text(critval+.5,.09, str(critval), rotation=90)
      
#     plt.xlabel('$\\lambda = \\log({\\cal L}_{\\mathbb{H}_{1}}/{\\cal L}_{\\mathbb{H}_{0}})$')
#     plt.ylabel('Probability')
#     plt.legend(loc = 2, framealpha = 0.3)
#     plt.xlim()
#     plt.tick_params(axis='both')
#     plt.title(title3)
#     plt.grid(True)

#     plt.show()
    
# Combined Plot LLR and Density

title4 = str(Nsets0) + " sets; " + str(Ngames0) + " games / set; " + str(Ncards0) + " cards / game; $\\mathbb{H}_{0}$: " + str(gimme0) + ", $\\mathbb{H}_{1}$: " + str(gimme1) + " cheater cards" 
             
 # make figure
fig, (ax1, ax2) = plt.subplots(1,2,figsize = [12.8, 4.8])
fig.suptitle(title4)
ax1.bar(Prob0[0], Prob0[1], width=1, facecolor='deepskyblue',
              alpha=0.5, label="$\\mathbb{H}_0$: gimme " + str(gimme0))
ax1.bar(Prob1[0], Prob1[1], width=1, facecolor='salmon',
              alpha=0.5, label="$\\mathbb{H}_1$: gimme " + str(gimme1))
ax2.hist(L_X, bins=np.arange(min(L_XY), max(L_XY) + binwidth, binwidth),
             facecolor='deepskyblue', density = True, alpha=0.5,
             label="$\\mathbb{H}_0$")
ax2.hist(L_Y, bins=np.arange(min(L_XY), max(L_XY) + binwidth, binwidth),
             facecolor='salmon', density = True, alpha=0.5,
             label="$\\mathbb{H}_1$")

plt.axvline(critval, color = 'black', linewidth = 1)
# plt.text(critval+.8,.09, str(critval), rotation=90)
    
ax1.set_title("Density vs Probability")
ax2.set_title("LLR vs Probability; $\\alpha = $" + str(alpha) + " @$\\lambda$ = " + str(critval) + "; $\\beta = $" + str(beta))
ax1.set(xlabel='Wins / Game', ylabel="Probability")
ax2.set(xlabel='$\\lambda = \\log({\\cal L}_{\\mathbb{H}_{1}}/{\\cal L}_{\\mathbb{H}_{0}})$', ylabel="Probability")
ax1.legend(loc=2, framealpha = 0.3)
ax1.tick_params(axis='both')
ax2.tick_params(axis='both')
ax1.grid(True)
ax2.grid(True)

plt.show()