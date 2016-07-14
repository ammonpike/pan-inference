#python
#requires panlex.py (from panlex_python_api)

import sys
import json
import panlex
import normScore

jsonIn = sys.argv[1] #name json input file
with open(jsonIn, 'r') as file:
    jsonObj = json.load(file)
    for pair in jsonObj:
        tempScore = normScore.d2Score(pair['ex1']['uid'], pair['ex1']['tt'], pair['ex2']['uid'], pair['ex2']['tt'])
        pair['scores']['TAgADD'] = tempScore
        tempScore = normScore.d2Geom(pair['ex1']['uid'], pair['ex1']['tt'], pair['ex2']['uid'], pair['ex2']['tt'])
        pair['scores']['TAgGeo'] = tempScore
        tempScore = normScore.d1Conf(pair['ex1']['uid'], pair['ex1']['tt'], pair['ex2']['uid'], pair['ex2']['tt'])
        pair['scores']['d1Conf'] = tempScore

with open(jsonIn, 'w') as file:
    json.dump(jsonObj, file, ensure_ascii=False)

