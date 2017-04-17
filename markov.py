import random

##EXAMPLE CHAIN
EXCHAIN = { "fish" : { 'food': 1, 'smell': 1}}

#flag for then end of the message.
TERMINAL = 345935


def build_chain(corpus : list):
    chain = {}
    for line in corpus:
        toks = line.split() + [TERMINAL]
        for i in range(len(toks)-1):
            #Make sure we have a dict for this key
            if(not toks[i] in chain):
                chain[toks[i]] = {}
            trunk = chain[toks[i]]
            #increment if this is a repeat leaf
            if(toks[i+1] in trunk):
                trunk[toks[i+1]]+=1
            #or add the leaf if it's novel
            else:
                trunk[toks[i+1]] = 1
    return chain


def clean_chain(chain):
    clean = []
    for k in chain:
        if(len(chain[k]) == 1):
            clean.append(k)
    for k in clean:
        del chain[k]


def run_chain(chain, start=None):
    if(start is None):
        start = random.choice(list(chain.keys()))
    msg = [start]
    while True:
        trunk = chain[msg[-1]]
        keys = trunk.keys()
        nxtTokList = []
        for k in keys:
            nxtTokList += [k]*trunk[k]
        nxtTok = random.choice(nxtTokList)
        if(nxtTok == TERMINAL): break
        msg.append(nxtTok)
    return ' '.join(msg)
