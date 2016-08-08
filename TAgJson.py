#python
#requires panlex.py (from panlex_python_api)

import sys
import json
import panlex
import normScore
import time

#Input file should have ex1, ex2 and score columns
#ex items should have tt, ex and uid in them
#score is hash with test as key, score as value
i = 0
jsonIn = sys.argv[1] #name json input file
with open(jsonIn, 'r') as file:
    jsonObj = json.load(file)
    for pair in jsonObj:
        try:
#            if 'TAgADD' in pair['scores']:
#                continue
#            else:
#                tempScore = normScore.d2Score(pair['ex1']['uid'], pair['ex1']['tt'], pair['ex2']['uid'], pair['ex2']['tt'])
#                pair['scores']['TAgADD'] = tempScore

#            if 'TAgCount' in pair['scores']:
#                continue
#            else:
#                tempScore = normScore.d2noTQ(pair['ex1']['uid'], pair['ex1']['tt'], pair['ex2']['uid'], pair['ex2']['tt'])
#                pair['scores']['TAgCount'] = tempScore

#            if 'TAgGeo' in pair['scores']:
#                continue
#            else:
#                tempScore = normScore.d2Geom(pair['ex1']['uid'], pair['ex1']['tt'], pair['ex2']['uid'], pair['ex2']['tt'])
#                pair['scores']['TAgGeo'] = tempScore

#            if 'd1Conf' in pair['scores']:
#                continue
#            else:
#                tempScore = normScore.d1Conf(pair['ex1']['uid'], pair['ex1']['tt'], pair['ex2']['uid'], pair['ex2']['tt'])
#                pair['scores']['d1Conf'] = tempScore

#            if 'd2Avg' in pair['scores']:
#                continue
#            else:
#                tempScore = normScore.d2Avg(pair['ex1']['uid'], pair['ex1']['tt'], pair['ex2']['uid'], pair['ex2']['tt'])
#                pair['scores']['d2Avg'] = tempScore

            if i < 10:
                tempScore = normScore.d2Hybrid(pair['ex1']['uid'], pair['ex1']['tt'], pair['ex2']['uid'], pair['ex2']['tt'], pair['scores']['tr2qa'])
                pair['scores']['d2Hybrid'] = tempScore
            
            i += 1
            if i == 30:
                time.sleep(3)
                i = 10
                print(tempScore)
            
        except:
            print("error detected, sleeping.")
            time.sleep(6)
with open(jsonIn, 'w') as file:
    json.dump(jsonObj, file, ensure_ascii=False)

