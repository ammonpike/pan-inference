#python
#requires panlex.py (from panlex_python_api)

import sys
import json
import panlex
import normScore

jsonIn = argv[1] #name json input file
with open(jsonIn, 'r') as file:
    jsonObj = json.load(file)
    for pair in jsonObj:
        tempScore = d2Score(pair['ex1']['uid'], pair['ex1']['tt'], pair['ex2']['uid'], pair['ex2']['tt'])
        jsonObj['pair']['scores']['TAg'] = tempScore
        
with open(jsonIn, 'w') as file:
    json.dump(jsonObj, file)
