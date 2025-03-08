import random
from pagerank import transition_model
from pagerank import sample_pagerank
from pagerank import iterate_pagerank
corpus={'5': set(),'1': {'2'}, '2': {'3', '1'}, '3': {'5', '2', '4'}, '4': {'2', '1'}}
appearance={}
damping_factor=0.85
n=10
a=iterate_pagerank(corpus,damping_factor) 
print(a)