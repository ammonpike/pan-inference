#python
#requires panlex.py (from panlex_python_api)

import sys
import json
import panlex
import time

#Scores translation of words at distance 2 in PanLex database
#Score is based on the ratio of the sum tq scores of the intersection
#   of all distance 1 translations from the source word to lang3 and
#   all translations from a target word in lang2 to lang3
#   to the sum of the union of the same.
#Scores for possible translations in language 2 will be ranked.
#Example call: python3 TranslationCheck.py cat eng-000 fra-000

limit = 100
secondLimit = 2
#command line arguments: source word, source language, target language. Optional: limit number of results, limit languages processed.
startWord = sys.argv[1]
lang1 = sys.argv[2]
lang3 = sys.argv[3]
if len(sys.argv) == 5:
    limit = int(sys.argv[4])
if len(sys.argv) == 6:
    secondLimit == int(sys.argv[5])

#From lang3, find all languages with d1 translations.
#Query is /ap "uid": lang3, "include": "lv"
#then change lang2 to be lv instead of uid?
targetParam = {"uid": lang3, "include": "lv",}
data = panlex.query("/ap",targetParam)
#time.sleep(5)
excludeQ = panlex.query("/lv", {"uid": lang3})
excludeR = excludeQ['result']
#print(excludeR)
exclude = excludeR[0]['lv']
#print(exclude)
langDict = {}

for source in data['result']:
    for choice in source['lv']:
        if choice != exclude:
            if choice in langDict:
                langDict[choice] += 1
            else:
                langDict[choice] = 1
#print(langDict)

lang2List = langDict.keys()

#pass list of d1 languages to d2 loop for scoring and list of lemmas.

#Start of loop for D2 translations
#lang2 should be lv of languages.
distance2Dict = {}
i = 0
for lang2 in lang2List:
    i += 1
#    print("start loop")
#    time.sleep(60)
    paramStart = {"lv":lang2,
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
#        time.sleep(60)
        word3 = word3Result['ex']
        
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
#        print(LangSearch)
        for word in LangSearch['result']:
            if word['uid'] in interLing:
                interLing[word['uid']] += 1
            elif word['uid'] != lang3: #exclude final target lang from jumps
                interLing[word['uid']] = 1
#        print(interLing)
        if len(interLing) == 0:
            continue
        #perform calculation on each intermediate language
        #perhaps put a safeguard discounting items with only one
        #intermediate item?
        tqSum = 0.00
        tqTotal = 0.00
        ling = list(interLing.keys())
#        print(ling)
#        print("Starting forward backward")
        forwardParam = {"uid":ling,
                        "truid":lang1,
                        "trtt":startWord,
                        "include":"trq",}
        backwardParam = {"uid":ling,
                        "trex":word3,
                        "include":"trq",}
#        time.sleep(10)            
        frontCheck = panlex.query("/ex", forwardParam)
#        time.sleep(10)
        backCheck = panlex.query("/ex", backwardParam)
    
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
    
        scores[word3] = tqSum / tqTotal
        if scores[word3] == 1:
            if len(front) == 1 and len(back) == 1:
#                print(tqSum)
                scores[word3] = tqSum / 18 #18 is max value of two entries
        print(str(word3) + " score of " + str(scores[word3]))

#Change this part so scores are stored in a file... somewhere.
#    resultList = sorted(scores, key=scores.__getitem__, reverse = True)
#    print("Scores for " + startWord + " in " + lang2 + ":")
#    for item in resultList:
#        x = item + ' with a score of ' + str(scores[item])
#        print(x)
    distance2Dict.update(scores)
    if i == secondLimit:
        break
#End of D2 Loop.

#Use list of D2 translations to find D1 translations into target language (lang3)
#Change D1 translations into decimal score (confidence score?)
finalQueryParam = {"uid": lang3,
                    "trex": list(distance2Dict.keys()),
                    "include":['trq'],
                    "sort": "trq desc",}
finalQuery = panlex.query("/ex",finalQueryParam)

d1Results = {}
totalTQ = 0.0
for result in finalQuery['result']:
    d1Results[result['tt']] = [result['trq'], result['trex']]
    totalTQ += result['trq']

for item in d1Results:
        d1Results[item][0] = int(d1Results[item][0]) / totalTQ
        
d3Results = {}
#print(d1Results)
#print(distance2Dict)
for word in d1Results:
    d3Results[word] = (d1Results[word][0] + distance2Dict[d1Results[word][1]]) / 2

resultList = sorted(d3Results, key=d3Results.__getitem__, reverse = True)
print("\n\nDistance 3 scores:")
for word in resultList:
    print(word + " score of " + str(d3Results[word]))
#Perform magic math to combine d1 score with d2 score.
#maybe multiply scores? Reflect: lower confidence in greater distance.
#or use D2 algorithm with D2 score standing in for weights on left, D1 on right
#Compare all translations of word to list of D2 translations (by language?, sum matches over total (weight is tq * d2 score?)