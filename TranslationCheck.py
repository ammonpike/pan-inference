#python
#requires panlex.py (from panlex_python_api)

import sys
import json
import panlex

#Scores translation of words at distance 2 in PanLex database
#Score is based on the ratio of the sum tq scores of the intersection
#   of all distance 1 translations from the source word to lang3 and
#   all translations from a target word in lang2 to lang3
#   to the sum of the union of the same.
#Scores for possible translations in language 2 will be ranked.
#Example call: python3 TranslationCheck.py cat eng-000 fra-000

limit = 100
#command line arguments: source word, source language, target language. Optional: limit number of results.
startWord = sys.argv[1]
lang1 = sys.argv[2]
lang2 = sys.argv[3]
if len(sys.argv) == 5:
    limit = int(sys.argv[4])

paramStart = {"uid":lang2,
              "truid":lang1,
              "trtt":startWord,
              "trdistance":2,
              "include":['trq', 'trpath'],
              "sort":'trq desc',
              "limit": limit,}
#distance 2 translation query
d2 = panlex.query("/ex",paramStart)

scores = {}

#process word by word
for word3Result in d2['result']:
    word3 = word3Result['tt']
    
    pathDict = {}
    #process each path to current word
    
    for pathSet in word3Result['trpath']:
        if pathSet[0]['ex2'] in pathDict:
            pathDict[pathSet[0]['ex2']] += 1
        else:
            pathDict[pathSet[0]['ex2']] = 1
    #retrieve lang codes for paths
    paramLang = {"ex":list(pathDict.keys()),
                 "include":"uid",}
    LangSearch = panlex.query("/ex",paramLang)
    interLing = {}
    
    for word in LangSearch['result']:
        if word['uid'] in interLing:
            interLing[word['uid']] += 1
        else:
            interLing[word['uid']] = 1
    
    #perform calculation on each intermediate language
    #perhaps put a safeguard discounting items with only one
    #intermediate item?
    lingResults = {}
    for ling in interLing.keys():
        tqSum = 0.00
        tqTotal = 0.00
    
        forwardParam = {"uid":ling,
                    "truid":lang1,
                    "trtt":startWord,
                    "include":"trq",}
        backwardParam = {"uid":ling,
                    "truid":lang2,
                    "trtt":word3,
                    "include":"trq",}
                    
        frontCheck = panlex.query('/ex', forwardParam)
        backCheck = panlex.query('/ex', backwardParam)
    
        front = {}
        back = {}

    #sort results of search into dictionaries for comparison
    #should I be using ex or tt? I used tt before but I guess if two
    #words in diff languages had the same orthography...
        for result in frontCheck['result']:
            if result['ex'] in front:
                front[result['ex']] += result['trq']
            else:
                front[result['ex']] = result['trq']
            
        for result in backCheck['result']:
            if result['ex'] in back:
                back[result['ex']] += result['trq']
            else:
                back[result['ex']] = result['trq']
            
        for word in front:
            if word in back:
                tqSum += front[word]
            tqTotal += front[word]
        for word in back:
            if word in front:
                tqSum += back[word]
            tqTotal += back[word]
        interLing[ling] = tqSum / tqTotal + 6
        
        
    scoreList = sorted(interLing, key=interLing.__getitem__, reverse = True)
    
    
    scores[word3] = interLing[scoreList[0]]
    print(word3 + " score of " + str(scores[word3]))

resultList = sorted(scores, key=scores.__getitem__, reverse = True)
print("\n\nScores for " + startWord + " in " + lang2 + ":")
for item in resultList:
    x = item + ' with a score of ' + str(scores[item])
    print(x)