#!/usr/bin/env python
# import sys
import numpy as np
import matplotlib.pyplot as plt
import math
# import time
NUM_LINES = 200000000#10000000

TrainFile = "../data/train" #sys.argv[1]
#TestFile = "test" #sys.argv[2]
OutFile = "out" #sys.argv[3]

def ComputeDwellTimes(Clicks, DwellTimes):
	for v in Clicks.values():
		DwellTimes.append(v)

def plotRepeatQueryPowerLaw(repeatQ_dict):
	repeatQ_X = sorted(repeatQ_dict.keys())
 	repeatQ_Y = [repeatQ_dict[x] for x in repeatQ_X]


 	#find the slope with polyfit
 	repeatQ_x_log = [math.log(x) for x in repeatQ_X if repeatQ_dict[x] > 2]
 	repeatQ_y_log = [math.log(y) for y in repeatQ_Y if y > 2 ]
 	m,b = np.polyfit(repeatQ_x_log,repeatQ_y_log,1)
 	power_law_line_y = [pow(x,m) *math.exp(b)  for x in repeatQ_X]
 	# print repeatQ_dict
 	plt.plot(repeatQ_X,repeatQ_Y,'ro',repeatQ_X,power_law_line_y)
 	plt.xlabel("Number of navigational queries")
 	plt.ylabel("Count")
 	plt.xscale('log')
 	plt.yscale('log')
 	plt.axis([2,max(repeatQ_X)*2, 1, max(repeatQ_Y)*2 ])
 	plt.title("Navigational queries")
 	print "slope of power law is ", m
 	plt.savefig('../figures/navigation_power_laws.png')
 	return sum(repeatQ_dict.values())


# def plotRepeatQueryPowerLaw(repeatedClicks):
# 	# print repeatedClicks
# 	repeatQ = 0
# 	repeatQ_X = [ ] # x value is basically v in the inner loop below
# 	repeatQ_Y = [ ] # Y values is the number of urlids that have same value for any user.
# 	repeatQ_dict = {}
# 	for userId in repeatedClicks:
# 		# print "we can optimize these clicks for %s" %(userId)
# 		for queryId in repeatedClicks[userId]:
# 			v = repeatedClicks[userId][queryId][1]
# 			if v > 1 :
# 				# print "userId: %s urlID: %svalue: %d" %(userId,queryId, v)
# 				repeatQ += v
# 				if v not in repeatQ_dict:
# 					repeatQ_dict[v] = 1
# 				else:
# 					repeatQ_dict[v] += 1

# 	repeatQ_X = sorted(repeatQ_dict.keys())
#  	repeatQ_Y = [repeatQ_dict[x] for x in repeatQ_X]


#  	#find the slope with polyfit
#  	repeatQ_x_log = [math.log(x) for x in repeatQ_X if repeatQ_dict[x] > 2]
#  	repeatQ_y_log = [math.log(y) for y in repeatQ_Y if y > 2 ]
#  	m,b = np.polyfit(repeatQ_x_log,repeatQ_y_log,1)
#  	power_law_line_y = [pow(x,m) *math.exp(b)  for x in repeatQ_X]
#  	# print repeatQ_dict
#  	plt.plot(repeatQ_X,repeatQ_Y,'ro',repeatQ_X,power_law_line_y)
#  	plt.xlabel("Number of navigational queries")
#  	plt.ylabel("Count")
#  	plt.xscale('log')
#  	plt.yscale('log')
#  	plt.axis([2,max(repeatQ_X)*2, 1, max(repeatQ_Y)*2 ])
#  	plt.title("Navigational queries")
#  	print "slope of power law is ", m
#  	plt.savefig('../figures/navigation_power_laws.png')
#  	print len(repeatedClicks), len(repeatQ_dict)
#  	return sum(repeatQ_dict.values())


def StoreDictionaryToFile(repeatedClicks, startDeletingFrom, currentUserID,repeatQ_dict, repeatQ, fHandle):
	for userId in xrange(startDeletingFrom, currentUserID):
		if userId in repeatedClicks:
			for queryId in repeatedClicks[userId]:
				tpl = repeatedClicks[userId][queryId]
				v = tpl[1]
				## only output if value is >= 2
				if v > 1:
					fHandle.write("%s:%s:%s\n" %(userId, queryId, tpl[0]))
					repeatQ += v
					if v not in repeatQ_dict:
						repeatQ_dict[v] = 1
					else:
						repeatQ_dict[v] += 1

			del repeatedClicks[userId]
	return (currentUserID, repeatQ)

def main():
	"""
	Use the fact that the training set is in order of userId's so periodically empty the dictionary
	also in plot function where we have to keep the whole data in memory then one can use
	numpy arrays
	"""
	# start = time.clock()
	f_rep_clicks = open("../data/store_repeatClickDict.txt", "w")
	with open(TrainFile) as train:
		#test = open(TestFile)
		count = 0
		# sessionIDs = set()
		# userIDs = set()
		# serpIDs = set() #Search Engine Results page id

		# urls = set()
		# domains = set()
		# queries = set() #query id
		# terms = set() # list of terms thata are part of the query
		repeatQ = 0
		# repeatQ_X = [ ] # x value is basically v in the inner loop below
		# repeatQ_Y = [ ] # Y values is the number of urlids that have same value for any user.
		repeatQ_dict = {}
		# DwellTimes = []
		currentSession = -1
		# currentClicks = dict()
		currentQuery = -1
		currentPage = -1
		qcnt = 0
		# currentTime = 0
		currentUserID = -1
		startDeletingFrom =0
		repeatedClicks = {}
		selectedTopRankedResult = None
		localUrlList = []
		for line in train:
			line = line.strip('\n')
			if count % (NUM_LINES/10000) == 0:
				print count / (NUM_LINES/10000)
			if count % (NUM_LINES/1000) == 0:
				(startDeletingFrom, repeatQ) = StoreDictionaryToFile(repeatedClicks, startDeletingFrom, currentUserID,repeatQ_dict, repeatQ, f_rep_clicks)
			if count > NUM_LINES:
				(startDeletingFrom, repeatQ) = StoreDictionaryToFile(repeatedClicks, startDeletingFrom, currentUserID,repeatQ_dict, repeatQ, f_rep_clicks)
				print (plotRepeatQueryPowerLaw(repeatQ_dict))*1.0/ qcnt
				break
			count += 1
			tokens = line.split('\t')
			session = int(tokens[0])
			if (currentSession >= 0 and currentPage != -1):
				# print "Entered first if"
				if (currentSession != session):
					# print "Entered inner if"
					# currentClicks[currentPage] = -1 # final click
					if currentUserID not in repeatedClicks:
						repeatedClicks[currentUserID] = {}
						if selectedTopRankedResult == False:
							repeatedClicks[currentUserID][currentQuery] = (currentPage,1)
					else:
						if currentQuery not in repeatedClicks[currentUserID] and selectedTopRankedResult == False:
							repeatedClicks[currentUserID][currentQuery] = (currentPage,1)
						if currentQuery in repeatedClicks[currentUserID] and selectedTopRankedResult == False:
							tpl = repeatedClicks[currentUserID][currentQuery]
							repeatedClicks[currentUserID][currentQuery] = (tpl[0], tpl[1] + 1)



				# ComputeDwellTimes(currentClicks, DwellTimes)
			currentPage = -1
			currentSession = session
				# currentClicks = dict()
				# currentTime = 0
			if (tokens[1] == "M"):
				# sessionIDs.add(session)
				# userIDs.add(tokens[3])
				currentUserID = int(tokens[3])
			elif (tokens[2] == "Q" or tokens[2] == "T"):
				# if currentUserID == "404":
				# 	print line
				qcnt += 1
				localUrlList = []
				#serpIDs.add(tokens[3])
				# queries.add(tokens[4])
				currentQuery = int(tokens[4])
				#listOfTerms = tokens[5].split(',')
				#for term in listOfTerms:
				#	terms.add(term)
				# currentTime = int(tokens[1])
				for i in range(6, len(tokens)):
					pair = tokens[i].split(',')

					# urls.add(pair[0])
					localUrlList.append(int(pair[0]))
					# domains.add(pair[1])
					# currentClicks[pair[0]] = 0
			elif (tokens[2] == "C"):
				# if currentUserID == "404":
				# if (currentPage != ""):
				# 	print line
					# currentClicks[currentPage] = int(tokens[1])-currentTime
				# currentTime = int(tokens[1])
				currentPage = int(tokens[4])
				#is current page top-ranked
				if currentPage != localUrlList[0]:
					selectedTopRankedResult = False
				else:
					selectedTopRankedResult = True




	#### lets save the repeatedClicks to file; so that we have the info
	### and can look up in O(1) time when we run the test set


	# for userId in repeatedClicks:
	# 	for queryId in repeatedClicks[userId]:
	# 		tpl = repeatedClicks[userId][queryId]
	# 		## only output if value is >= 2
	# 		if tpl[1] > 2:
	# 			f_rep_clicks.write("%s:%s:%s\n" %(userId, queryId, tpl[0]))

	### once we have finished reading the file in
	(startDeletingFrom, repeatQ) = StoreDictionaryToFile(repeatedClicks, startDeletingFrom, currentUserID,repeatQ_dict, repeatQ, f_rep_clicks)
	print (plotRepeatQueryPowerLaw(repeatQ_dict))*1.0/ qcnt
	f_rep_clicks.close()

 ######### COMMENTED OUT FOR NOW #####
		# print "Total clicks:", len(DwellTimes)
		# DwellTimes = np.array(DwellTimes)
		# maxTime = np.amax(DwellTimes)
		# for i in range(0,len(DwellTimes)):
		# 	if (DwellTimes[i] == -1):
		# 		DwellTimes[i] = maxTime

		# X = np.array(range(1,np.amax(DwellTimes)+1))
		# Y = np.bincount(DwellTimes)[1:].astype(float)
		# Ysum = np.sum(Y)
		# #Y /= Ysum
		# OutF = open(OutFile, 'w')
		# for i in range(len(X)):
		# 	if (Y[i] == 0):
		# 		continue
		# 	else:
		# 		OutF.write("%f %f\n" % (X[i], Y[i]))
		# OutF.close()

	# end = time.clock()
	# repeatQ = plotRepeatQueryPowerLaw(repeatedClicks)
	# print end - start
	# print "Session IDs:", len(sessionIDs)
	# print "User IDs:", len(userIDs)
	# print "SERP IDs:", len(serpIDs)

	# print "URLs:", len(urls)
	# print "Queries:", len(queries)
	#print "Fraction of queries ", repeatQ*1.0/len(queries)
	# print "Domains:", len(domains)
	#test.close()

if __name__ == '__main__':
	main()