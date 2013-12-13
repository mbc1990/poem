from random import randint
from random import choice
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import fuzzy
import Levenshtein as pylev
from stat_parser import Parser
parser = Parser()



#corpuses = ['god_and_the_state.txt','age_of_fable.txt', 'golden_bough.txt', 'custom_myth.txt']
corpuses = ['god_and_the_state.txt']
#corpuses = ['dummy_corpus.txt']
#corpuses = ['sad.txt']
tmap = {}

def build_model(tokens, n):
    global tmap
    for i in range(0, len(tokens) - n):
        if tuple(tokens[i:i+n]) not in tmap:
            tmap[tuple(tokens[i:i+n])] = []
        tmap[tuple(tokens[i:i+n])].append(tokens[i+n])

def generate_text(n, length):
    keys = tmap.keys()
    start = keys[randint(0, len(keys)-1)]
    while start[0] in [',', '.', '!', '?', '\'']:
        start = keys[randint(0, len(keys)-1)]
    ret = list(start)
    while len(ret) < length:
        lastn = ret[-2:]
        try:
            nextword = choice(tmap[tuple(lastn)])
            ret.append(nextword)        
        except:
            length = 0
            pass
    return ret


def print_human_text(tokens):
    outpt = ""
    for t in tokens:
        if len(outpt) != 0 and t not in [',', '.', '!']:
            outpt += " "
        outpt += t
    print outpt


def generate_poem(n):
    keys = tmap.keys()
    start = keys[randint(0, len(keys))]
    num_lines = randint(2,5)
    poem = []
    for i in range(0,num_lines):
        num_toks = randint(1,5)
        poem.append( generate_text(n, num_toks) )
    for i in poem:
        print_human_text(i)


         
def calc_sim(candidate, poem, sim_range):
    inrange = [] #lines within sim_range
    if len(poem) <= sim_range:
        inrange = poem
    else:
        inrange = poem[-sim_range:]
    score = 0 
    for line in poem:
        for tok in line:
            for can_tok in candidate:
                score += pylev.distance( fuzzy.nysiis(tok), fuzzy.nysiis(can_tok))
    return score

         

def generate_word_similar_text(poem, iters, sim_range, n, num_toks):
    candidates = [generate_text(n, num_toks) for i in range(0, iters)]
    sorted(candidates, key=lambda x: calc_sim(x, poem, sim_range))     
    return candidates[0]

    

#n - ngrams used to build model
#word_sim_freq - number in range of 0-10 of how frequently the word_similarity heuristic should be applied
#word_sim_iters - number of lines that are generated of which the best is chosen 
#word_sim_range - how many lines back the word sim looks
def generate_cohesive_poem(n, word_sim_freq, word_sim_iters, word_sim_range): 
    num_lines = randint(2,5)
    poem = []
    total_word_sim = 0
    for i in range(0,num_lines):
        num_toks = randint(1,3)
        if randint(0,10) < word_sim_freq:
            poem.append( generate_word_similar_text(poem, word_sim_iters, word_sim_range, n, num_toks) )
            total_word_sim += 1
        else:
            poem.append( generate_text(n, num_toks) )

#    for i in poem:
 #       print_human_text(i)
    return poem
#    print("Lines sim'd: "+str(total_word_sim))

def poem_height(cand):
    fulltext = [word for line in cand for word in line]
    fullstr = ''
    for w in fulltext:
        fullstr += w+' '
    try:
        ptree = parser.parse(fullstr)
        return ptree.height()
    except:
        return 0 #unparsable? parser throws an exception sometimes, complaining about chomsky normal form
     
def main():
    #tweaking
    n_size = 2
    word_sim_chance = 5
    word_sim_cand = 250
    word_sim_range = 5
    min_parse_depth = 7
    #
    
    tokens = []
    for c in corpuses:
        with open(c) as fd:
            content = fd.read()
            tokens += [word for sent in sent_tokenize(content) for word in word_tokenize(sent)] 
    build_model(tokens, n_size)
    print ""
    poems = []
    for i in range(0, 5):
        cand = generate_cohesive_poem(n_size, word_sim_chance, word_sim_cand, word_sim_range) #n=2, %*10 chance of word-sim, # of word-sim candidates, wordsim range
        while(poem_height(cand) < min_parse_depth):
            cand = generate_cohesive_poem(n_size, word_sim_chance, word_sim_cand, word_sim_range)
            print "Generated poem lacks parse depth, retrying..."
        poems.append(cand)
    print " "
    for p in poems:
        for i in p:
            print_human_text(i)
        print " "
        

if __name__ == "__main__":
    main()
