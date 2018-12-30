import sys
import string
import argparse

import nltk
from nltk import grammar
from nltk import Tree
import nltk.tokenize

import cnf

global cnf_grammar
global sentences

#Check whether two trees represent the same parse.
def check_duplicate(tree1, tree2):
    match = True
    if len(tree1) == len(tree2):
        for i in range(len(tree1)):
            if tree1[i] in tree1.leaves() and tree2[i] in tree2.leaves():
                if not tree1[i] == tree2[i]:
                    match = False
            elif not check_duplicate(tree1[i], tree2[i]):
                match = False
    else:
        return False
    return match

#Read grammar and sentences to parse from files.
def init(grammar_file, sentence_file):
    global cnf_grammar, sentences
    cnf_grammar = cnf.convert(grammar_file)
    f = open(sentence_file)
    sentences = f.readlines()

#Parse using cky algorithm.
def parse(words):
    n = len(words)
    #create table
    table = []
    for i in range(n+1):
        table.append([])
        for j in range(n+1):
            table[i].append([])

    for j in range(1, n+1):
        table[j-1][j] += findtrees_from_terminal(words[j-1])
        r = range(0, n-1)
        r.reverse()
        for i in r:
            for k in range(i+1, j):
                for tree1 in table[i][k]:
                    for tree2 in table[k][j]:
                        parselist = findparse_from_trees(tree1, tree2)
                        for parse in parselist:
                            table[i][j].append(parse)

    return table

#Find nonterminal(s) for 2 nonterminals.
def findparse_from_trees(tree1, tree2):
    ret_list = []
    for production in cnf_grammar.productions():
        if (production.rhs()[0] == tree1.label()
            and production.rhs()[-1] == tree2.label()):
            ret_list.append(Tree(production.lhs(), [tree1, tree2]))
    return ret_list

#Find nonterminal(s) for terminal.
def findtrees_from_terminal(word):
    ret_list = []
    for production in cnf_grammar.productions():
        if word in production.rhs():
            ret_list.append(Tree(production.lhs(), [word]))
    return ret_list

#Print the list of parses.
def printfinal(table):
    parse_list = table[0][-1]

    #Remove duplicates.
    for i in range(len(parse_list)-1):
        for j in parse_list[i+1:]:
            if check_duplicate(parse_list[i], j):
                parse_list.remove(j)

    for parse in table[0][-1]:
        print(parse)
    print("Number of parses: " + str(len(table[0][-1])))
    return len(table[0][-1])

def main():
    global cnf_grammar, sentences

    #Parse arguments.
    parser = argparse.ArgumentParser(description = 'An implementation of the CKY parsing algorithm.')
    parser.add_argument('grammar', type=str, help='path to a CFG file')
    parser.add_argument('sentences', type=str,
                        help='path to a text file with sentences to parse')
    args = parser.parse_args()

    init(args.grammar, args.sentences)
    for sentence in sentences:
        #Tokenize.
        words = nltk.word_tokenize(sentence)
        #Parse/\.
        table = parse(words)
        print(sentence[:-1])
        printfinal(table)
        if sentences.index(sentence) != len(sentences)-1:
            print("\n")

main()
