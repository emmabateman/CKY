import re
import random
import nltk
from nltk import grammar

N = [] #nonterminals
sigma = [] #terminals
R = [] #rules
marked_for_deletion = []

#Load CFG from file into global vars.
def get_cfg(filename):
    global N, sigma, R

    my_grammar = nltk.data.load(filename)

    for p in my_grammar.productions():
        N.append(p.lhs().symbol()) #add nonterminal
        for element in p.rhs():
            if grammar.is_terminal(element):
                sigma.append(element) #add rhs terminal(s)
            else:
                N.append(element.symbol()) #add rhs nonterminal(s)
        R.append(p) #add rule

    #remove duplicates
    N = list(set(N))
    sigma = list(set(sigma))

#Determine whether production is already in Chomsky Normal Form.
def is_cnf(production):
    rhs = production.rhs()

    if len(rhs) == 1:
        return grammar.is_terminal(rhs[0])
    elif len(rhs) == 2:
        return (grammar.is_nonterminal(rhs[0])
               and grammar.is_nonterminal(rhs[1]))
    else:
        return False

#Determine whether production is a unit production. (e.g. A -> B)
def is_unit(production):
    if (len(production.rhs()) == 1
       and grammar.is_nonterminal(production.rhs()[0])):

        return True
    else:
        return False

#Replace unit production of form A -> B by adding rule A -> rhs
# for every rule B -> rhs.
def repl_unit(A, B):
    for rule in R:
        if rule.lhs() == B:
            R.append(grammar.Production(A, rule.rhs()))

#Replace terminals on right hand side of production by substituting
# with dummy nonterminals.
# (e.g. [A -> B b] becomes [A -> B C] and [C -> b])
def remove_rhs_terminals(production):
    rhs = production.rhs()
    if len(rhs) > 1:
        new_rhs = ()
        for element in rhs:
            if grammar.is_terminal(element):
                #create dummy nonterminal
                new_nt = grammar.Nonterminal(create_nonterminal())
                new_rhs = new_rhs + (new_nt,)

                #define dummy nonterminal
                R.append(grammar.Production(new_nt, (element,)))
            else:
                new_rhs = new_rhs + (element,)

        #replace rule
        R[R.index(production)] = grammar.Production(production.lhs(), new_rhs)

#Choose random name for new nonterminal.
def create_nonterminal():
    while True:
        string = "_"
        for i in range(3):
            string += str(unichr(random.randint(ord('A'), ord('Z'))))
        if not string in N:
            N.append(string)
            return string

#Shorten long productions by splitting them into two new productions.
def shorten(production):
    lhs = production.lhs()
    rhs = production.rhs()
    if len(rhs) > 2: #it's too long
        new_nt = grammar.Nonterminal(create_nonterminal())
        new_production_1 = grammar.Production(lhs, (rhs[0], new_nt))
        new_rhs = ()
        for i in range(1, len(rhs)):
            new_rhs = new_rhs + (rhs[i],)

        new_production_2 = grammar.Production(new_nt, new_rhs)
        
        marked_for_deletion.append(production)

        R.append(new_production_1)
        R.append(new_production_2)

def convert(filename):
    global R, marked_for_deletion
    get_cfg(filename)

    #replace rhs terminals with dummy nonterminals
    for rule in R:
        remove_rhs_terminals(rule)

    #eliminate unit productions
    marked_for_deletion = []
    for rule in R:
        if is_unit(rule):
            marked_for_deletion.append(rule)
            A = rule.lhs()
            B = rule.rhs()[0]
            repl_unit(A, B)
    for rule in marked_for_deletion:
        R.remove(rule)

    #shorten long rules
    marked_for_deletion = []
    for rule in R:
        shorten(rule)
    for rule in marked_for_deletion:
        R.remove(rule)
   
    new_grammar = grammar.CFG(nltk.data.load(filename).start(), R)
    if not new_grammar.is_chomsky_normal_form():
        sys.stderr.write("conversion to Chomsky Normal Form failed!")
    
    return new_grammar
