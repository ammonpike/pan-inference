#python
#requires panlex.py (from panlex_python_api)

import sys
import json
import panlex

#Methods for scoring translation of words at distance 2 in PanLex database
#Function call requires source UID, source TT, target UID, target TT.
#More efficient to use translationAgg.py for numerous calls
#These are all really quite super inefficient, 
#but they are designed to get the numbers
#for testing. Optimization can happen later.

#simple (now out of date) method for scoring distance one as basis for distance 2 translations
def d1Conf(lang1, startWord, lang2, endWord):   
    queryParam = {"uid":lang2, 
                "trtt":startWord, 
                "trtt": lang1, 
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

#As above, but uses lv instead of uid for target language        
def d1ConfF(lang1, startWord, lv2, endWord):   
    queryParam = {"lv":lv2, 
                "trtt":startWord, 
                "truid": lang1, 
                "include":['trq'], 
                "sort":"trq desc"}
    query = panlex.query('/ex', queryParam)

    totalTQ = 0
    results = {}

    for word in query['result']:
        results[word['ex']] = word['trq']
        totalTQ += word['trq']

    for word in results:
        results[word] = results[word] / totalTQ
    if endWord in results:
        return results[endWord]
    else:
        return 0.00

#as above, uses lv instead of uid for source language
def d1ConfB(lv1, startWord, lang2, endWord):   
    queryParam = {"uid":lang2, 
                "trex":startWord, 
                "trlv": lv1, 
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

#Main d2 scoring method. Based on "translationAgg.py" algorithm
#Finds ratio of same translations in intermediary language to set of all translations in intermediary language
#Uses ratio as score
#Used as weight in another test, reimplemented.
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
        if pathSet[0]['lv2'] in pathDict:
            pathDict[pathSet[0]['lv2']] += 1
        else:
            pathDict[pathSet[0]['lv2']] = 1

    #perform calculation on each intermediate language
    #perhaps put a safeguard discounting items with only one
    #intermediate item?
    tqSum = 0.00
    tqTotal = 0.00
    ling = list(pathDict.keys())
    forwardParam = {"lv":ling,
                    "truid":lang1,
                    "trtt":startWord,
                    "include":"trq",}
    backwardParam = {"lv":ling,
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

#Out of date test--uses raw count instead of TQ for scores
def d2noTQ(lang1, startWord, lang2, endWord):
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
        if pathSet[0]['lv2'] in pathDict:
            pathDict[pathSet[0]['lv2']] += 1
        else:
            pathDict[pathSet[0]['lv2']] = 1

    #perform calculation on each intermediate language
    #perhaps put a safeguard discounting items with only one
    #intermediate item?
    tqSum = 0.00
    tqTotal = 0.00
    ling = list(pathDict.keys())
    forwardParam = {"lv":ling,
                    "truid":lang1,
                    "trtt":startWord,
                    "include":"trq",}
    backwardParam = {"lv":ling,
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
            front[result['ex']] += 1
        else:
            front[result['ex']] = 1
            
    for result in backCheck['result']:
        if result['ex'] in back:
            back[result['ex']] += 1
        else:
            back[result['ex']] = 1
            
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
    score = tqSum / (tqTotal) #best smoothing number to date
    #+ 1? That would curve the 1.0 scores (very) slightly.
    #Actually, it would have greater impact the smaller the sample size. It could even be + 2 (one one-ranked for each side)
#    if scores[endWord] == 1:
#        if len(front) == 1 and len(back) == 1:
#            print(tqSum)
#            scores[endWord] = tqSum / 18 #18 is max value of two dictionary entries
    return score
    
#using geometric mean? Results seem to be worse though. Out of date
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
        if pathSet[0]['lv2'] in pathDict:
            pathDict[pathSet[0]['lv2']] += 1
        else:
            pathDict[pathSet[0]['lv2']] = 1
    
    tqSum = 0.00
    tqTotal = 0.00
    ling = list(pathDict.keys())
    forwardParam = {"lv":ling,
                    "truid":lang1,
                    "trtt":startWord,
                    "include":"trq",}
    backwardParam = {"lv":ling,
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
    
#what about an average of d1conf * d1conf? Find both confidence, multiply, sum all paths and divide by number of paths?
#need uid and tt of intermediate words
#Uses above d1Conf scores
#Out of date
def d2Avg(lang1, startWord, lang2, endWord):
    paramStart = {"uid":lang2,
                "tt":endWord,
                "truid":lang1,
                "trtt":startWord,
                "trdistance":2,
                "include":['trq', 'trpath'],
                "sort":'trq desc',
                }
    d2 = panlex.query("/ex",paramStart)
    
    #perhaps do max() instead of average. average gets really low results (something Jonathan doesn't like)
    count = 0
    tqSum = 0.00
    for word in d2['result'][0]['trpath']:
        tempScore = d1ConfF(lang1, startWord, word[0]['lv2'], word[0]['ex2']) * d1ConfB(word[0]['lv2'], word[0]['ex2'], lang2, endWord)
        count += 1
        tqSum += tempScore
    score = tqSum / count
    return score
#        if tempScore > count:
#            count = tempScore
#    return count

    
#function for combining tr2qa and d2Score
#Basically do the d2Score, but while calculating note lv of intermediate languages
#retrieve max d1 scores for each lv change
#divide tr2qa (score provided by PanLex) by maxD2 (estimated maximum tr2qa)
#multiply by weight--d2Score result
#Final test run, shows results are less trustworthy.
def d2Hybrid(lang1, startWord, lang2, endWord, qaScore):
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
        if pathSet[0]['lv2'] in pathDict:
            pathDict[pathSet[0]['lv2']] += 1
        else:
            pathDict[pathSet[0]['lv2']] = 1

    #right here grab lv of each step
    #find max D1 for each lv
    #determine max D2 for translation pair
    #also requires tr2qa score for pair
    leftSum = 0
    rightSum = 0
    
    #for intermediateLV in pathDict.keys():
    #    get lv1 to intermediateLV max score
    #    leftSum += tempLeft
    #    get intermediateLV to lv2 max score
    #    rightSum += tempRight
    tr2Max = sqrt(leftSum * rightSum)
    
    norm2qa = qaScore / tr2Max
    #perform calculation on each intermediate language
    #perhaps put a safeguard discounting items with only one
    #intermediate item?
    tqSum = 0.00
    tqTotal = 0.00
    ling = list(pathDict.keys())
    forwardParam = {"lv":ling,
                    "truid":lang1,
                    "trtt":startWord,
                    "include":"trq",}
    backwardParam = {"lv":ling,
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
        tqTotal += front[word]
    for word in back:
        tqTotal += back[word]
    score = tqSum / (tqTotal + 6) #best smoothing number to date
    
    #finally calculate hybrid score
    hybrid = score * norm2qa

    return hybrid
