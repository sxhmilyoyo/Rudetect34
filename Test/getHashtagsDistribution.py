import math
import matplotlib.pyplot as plt
import json
import operator
import pickle
from pprint import pprint

def getPlot(sorted_d):
	x = [i[0] for i in sorted_d]
	y = [i[1] for i in sorted_d]
	plt.plot(x, y)
	plt.xticks(x, [int(i[0]) for i in sorted_d])
	plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
	plt.show()
	# plt.savefig(os.path.join(self.rootPath, filePath, filename), bbox_inches='tight')
	# plt.clf()

def meanSd(tmp):
	mean = sum(tmp) / len(tmp)
	sd = math.sqrt(sum([(xi - mean)**2 for xi in tmp]) / (len(tmp) - 1))
	return round(mean, 2), round(sd, 2)

with open("../Data/hashtagsDistribution.json") as fp:
	data = json.load(fp)

# print result

new_d = {}
for k in data:
	new_d[int(k)] = data[k]
sorted_d = sorted(new_d.items(), key=operator.itemgetter(0), reverse=True)
# print sorted_d
# with open("../Data/sorted_hashtagsDistribution.json", "w") as fp:
# 	json.dump(sorted_d, fp, indent=4)



with open("../Data/TotalHashtags_test.pkl") as fp:
	totalHashtags = pickle.load(fp)

# filter
hashtags = [i[0] for i in totalHashtags if i[1] == 1]
# res = [h for h in hashtags if len(h.split()) <= 4]
# print len(res)

# a = []
# d = dict(totalHashtags)
# for i in res:
# 	a.append(d[i])
# m, sd = meanSd(a)
# print m, sd


pprint(hashtags)