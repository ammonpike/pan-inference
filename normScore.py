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
#Function call requires source UID, source TT, target UID, target TT.
#More efficient to use translationAgg.py for numerous calls
#Super inefficient, but a good start. Does the job.

#Input file should have ex1, ex2 and score columns
#ex items should have tt, ex and uid in them
#score is hash with test as key, score as value
def d1Conf(lang1, startWord, lang2, endWord):   
    queryParam = {"uid":lang2, 
                "trtt":startWord, 
                "truid": lang1, 
                "include":['trq'], 
                "sort":"trq desc"}
    query = panlex.query('/ex', queryParam)

    totalTQ = 0
    results = {}

    for word in query['result']:
        results[word['tt']] = word['trq']
        totalTQ += word['trq']

    for word in results:
        results[word] = results[word] / totalTQ
    if endWord in results:
        return results[endWord]
    else:
        return 0.00

def d2Score(lang1, startWord, lang2, endWord):
    paramStart = {"uid":lang2,
                "tt":endWord,
                "truid":lang1,
                "trtt":startWord,
                "trdistance":2,
                "include":['trq', 'trpath'],
                "sort":'trq desc',
                }
    d2 = panlex.query("/ex",paramStart)
    pathDict = {}
    for pathSet in d2['result'][0]['trpath']:
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
    tqSum = 0.00
    tqTotal = 0.00
    ling = list(interLing.keys())
    forwardParam = {"uid":ling,
                    "truid":lang1,
                    "trtt":startWord,
                    "include":"trq",}
    backwardParam = {"uid":ling,
                    "truid":lang2,
                    "trtt":endWord,
                    "include":"trq",}
                    
    frontCheck = panlex.query('/ex', forwardParam)
    backCheck = panlex.query('/ex', backwardParam)
    
    front = {}
    back = {}

    #sort results of search into dictionaries for comparison
    #should I be using ex or tt? I used tt before but I guess if two
    #words in diff languages had the same orthography...
    for result in frontCheck['result']:
#        print(result['tt'])
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
            tqSum += back[word]
#            if len(front) == 1:
#                print(front[word])
#            if len(back) == 1:
#                print(back[word])
        tqTotal += front[word]
    for word in back:
        tqTotal += back[word]    #theoretically, could the two above steps be combined?
    #For example, add result to trq AND tqTotal
    #Can items be 'in' JSON objects? Is it efficient?
    score = tqSum / (tqTotal + 6) #best smoothing number to date
    #+ 1? That would curve the 1.0 scores (very) slightly.
    #Actually, it would have greater impact the smaller the sample size. It could even be + 2 (one one-ranked for each side)
#    if scores[endWord] == 1:
#        if len(front) == 1 and len(back) == 1:
#            print(tqSum)
#            scores[endWord] = tqSum / 18 #18 is max value of two dictionary entries
    return score
    
    
def d2Geom(lang1, startWord, lang2, endWord):
    paramStart = {"uid":lang2,
                "tt":endWord,
                "truid":lang1,
                "trtt":startWord,
                "trdistance":2,
                "include":['trq', 'trpath'],
                "sort":'trq desc',
                }
    d2 = panlex.query("/ex",paramStart)
    pathDict = {}
    for pathSet in d2['result'][0]['trpath']:
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
    tqSum = 0.00
    tqTotal = 0.00
    ling = list(interLing.keys())
    forwardParam = {"uid":ling,
                    "truid":lang1,
                    "trtt":startWord,
                    "include":"trq",}
    backwardParam = {"uid":ling,
                    "truid":lang2,
                    "trtt":endWord,
                    "include":"trq",}
                    
    frontCheck = panlex.query('/ex', forwardParam)
    backCheck = panlex.query('/ex', backwardParam)
    
    front = {}
    back = {}

    #sort results of search into dictionaries for comparison
    #should I be using ex or tt? I used tt before but I guess if two
    #words in diff languages had the same orthography...
    for result in frontCheck['result']:
#        print(result['tt'])
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
            tqSum += (front[word] * back[word]) ** 0.5
#            if len(front) == 1:
#                print(front[word])
#            if len(back) == 1:
#                print(back[word])
        tqTotal += front[word]
    for word in back:
        tqTotal += back[word]
    #theoretically, could the two above steps be combined?
    #For example, add result to trq AND tqTotal
    #Can items be 'in' JSON objects? Is it efficient?
    score = tqSum / (tqTotal / 2 + 6) #best smoothing number to date
    #+ 1? That would curve the 1.0 scores (very) slightly.
    #Actually, it would have greater impact the smaller the sample size. It could even be + 2 (one one-ranked for each side)
#    if scores[endWord] == 1:
#        if len(front) == 1 and len(back) == 1:
#            print(tqSum)
#            scores[endWord] = tqSum / 18 #18 is max value of two dictionary entries
    return score