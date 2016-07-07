import panlex
import sys

word1 = sys.argv[1]
lang1 = sys.argv[2]
lang2 = sys.argv[3]

queryParam = {"uid":lang2, 
            "trtt":word1, 
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

sortedList = sorted(results, key=results.__getitem__, reverse = True)

for word in sortedList:
    print(word + ": " + str(results[word]) + "\n\n")