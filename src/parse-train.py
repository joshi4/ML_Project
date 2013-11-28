#!/usr/bin/env python
# import sys
import numpy as np

NUM_LINES = 100000#10000000

TrainFile = "../data/train" #sys.argv[1]
#TestFile = "test" #sys.argv[2]
OutFile = "out" #sys.argv[3]

def ComputeDwellTimes(Clicks, DwellTimes):
	for v in Clicks.values():
		DwellTimes.append(v)

with open(TrainFile) as train:
	#test = open(TestFile)
	count = 0
	sessionIDs = set()
	userIDs = set()
	serpIDs = set() #Search Engine Results page id
	urls = set()
	domains = set()
	queries = set() #query id
	terms = set() # list of terms thata are part of the query
	DwellTimes = []
	currentSession = -1
	currentClicks = dict()
	currentTime = 0
	currentPage = ""
	currentUserID = -1
	repeatedClicks = {}
	selectedTopRankedResult = None
	localUrlList = []
	for line in train:
		if count % (NUM_LINES/10) == 0:
			print count / (NUM_LINES/10)
		if count > NUM_LINES:
			break
		count += 1
		tokens = line.split('\t')
		session = int(tokens[0])
		if (currentSession != session):
			if (currentSession >= 0 and currentPage != ""):
				currentClicks[currentPage] = -1 # final click
				if currentUserID not in repeatedClicks:
					repeatedClicks[currentUserID] = {}
					repeatedClicks[currentUserID][currentPage] = 1
				else:
					if currentPage not in repeatedClicks[currentUserID]:
						repeatedClicks[currentUserID][currentPage] = 1
					else:
						repeatedClicks[currentUserID][currentPage] += 1



			ComputeDwellTimes(currentClicks, DwellTimes)
			currentSession = session
			currentPage = ""
			currentClicks = dict()
			currentTime = 0
		if (tokens[1] == "M"):
			sessionIDs.add(session)
			userIDs.add(tokens[3])
			currentUserID = tokens[3]
		elif (tokens[2] == "Q" or tokens[2] == "T"):
			localUrlList = []
			#serpIDs.add(tokens[3])
			queries.add(tokens[4])
			#listOfTerms = tokens[5].split(',')
			#for term in listOfTerms:
			#	terms.add(term)
			currentTime = int(tokens[1])
			for i in range(6, len(tokens)):
				pair = tokens[i].split(',')
				urls.add(pair[0])
				localUrlList.append(pair[0])
				domains.add(pair[1])
				currentClicks[pair[0]] = 0
		elif (tokens[2] == "C"):
			if (currentPage != ""):
				currentClicks[currentPage] = int(tokens[1])-currentTime
			currentTime = int(tokens[1])
			currentPage = tokens[4]
			#is current page top-ranked
			if currentPage != localUrlList[0]:
				selectedTopRankedResult = False
			else:
				selectedTopRankedResult = True



	print "Total clicks:", len(DwellTimes)
	DwellTimes = np.array(DwellTimes)
	maxTime = np.amax(DwellTimes)
	for i in range(0,len(DwellTimes)):
		if (DwellTimes[i] == -1):
			DwellTimes[i] = maxTime

	X = np.array(range(1,np.amax(DwellTimes)+1))
	Y = np.bincount(DwellTimes)[1:].astype(float)
	Ysum = np.sum(Y)
	#Y /= Ysum
	OutF = open(OutFile, 'w')
	for i in range(len(X)):
		if (Y[i] == 0):
			continue
		else:
			OutF.write("%f %f\n" % (X[i], Y[i]))
	OutF.close()

	# print "Session IDs:", len(sessionIDs)
	# print "User IDs:", len(userIDs)
	# print "SERP IDs:", len(serpIDs)
	print "URLs:", len(urls)
	print "Queries:", len(queries)
	print "Domains:", len(domains)
	#test.close()