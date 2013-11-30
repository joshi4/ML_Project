#!/usr/bin/env python

NUM_NAVIG_LINES = 8500000
NUM_TEST_LINES = 3000000
def freeDict(d):
    keys = d.keys()
    for k in keys:
        print "deleting: ", k
        del d[k]

def writeToSubmitFile(f_submit, currentSession, localUrlList):
    for url in localUrlList:
        f_submit.write("%d,%d\n"%(currentSession, url))

def loadNavigDict( navig_file):
    cnt = 0
    navigationalDict = { }

    with open(navig_file, "r") as f_navig:

        for line in f_navig:
            line = line.split("\n")
            keys_values = line[0].split(":")
            #converting to int is way better than keeping them as strings
            #saves a lot of space.
            userID = int(keys_values[0])
            queryId = int(keys_values[1])
            resultPage = int(keys_values[2])

            if userID not in navigationalDict:
                navigationalDict[userID] = {queryId: resultPage}
            else:
                navigationalDict[userID][queryId] = resultPage


            if cnt % (NUM_NAVIG_LINES/10000) == 0 :
                print cnt/((NUM_NAVIG_LINES/10000))
            if cnt > NUM_NAVIG_LINES:
                break
            cnt +=1
    return  navigationalDict

def deleteUnwantedKeys(startDeletingFrom, currentUserID, navigationalDict):
    for i in xrange(startDeletingFrom,currentUserID):
        if i in navigationalDict:
            del navigationalDict[i]
    return currentUserID


def parseTest(test_file, submit_file, navigationalDict):
    count = 0
    modifiedQueryCount = 0
    qcnt = 0
    currentSession = -1
    currentQuery = -1
    # currentPage = -1
    currentUserID = -1
    startDeletingFrom = 0
    localUrlList = [] # to deal with pesky scope issues.

    f_submit = open(submit_file, "w")
    f_submit.write("SessionID,URLID\n")
    with open(test_file) as test:
        for line in test:
            line = line.strip('\n')
            if count % (NUM_TEST_LINES/1000) == 0:
                print count / (NUM_TEST_LINES/1000)
                startDeletingFrom = deleteUnwantedKeys(startDeletingFrom, currentUserID, navigationalDict)

            if count > NUM_TEST_LINES:
                break

            tokens = line.split('\t')

            # if(currentSession >= 0 and currentPage != -1):
            #     if (currentSession != session):
            #         #delete the relevant keys from the navigational
            #         #Dict don't need it anymore:
            #         del navigationalDict[currentUserID]

            # currentSession = session

            if (tokens[1] == "M"):
                currentSession = int(tokens[0])
                currentUserID = int(tokens[3])
            if (tokens[2] == "T"):
                qcnt+=1
                writtenToSubmit = False
                localUrlList = []
                currentQuery = int(tokens[4])
                for i in range(6,len(tokens)):
                    pair = tokens[i].split(',')
                    localUrlList.append(int(pair[0]))

                if currentUserID in navigationalDict:
                    v = navigationalDict[currentUserID]
                    if currentQuery in v:
                        # print v[currentQuery], type(v[currentQuery])
                        pg = v[currentQuery]
                        #delete that particular entry and
                        #bump it to the top.
                        if pg in localUrlList and pg != localUrlList[0]:
                            localUrlList.remove(int(pg))
                            localUrlList.insert(0,pg)
                            writeToSubmitFile(f_submit, currentSession, localUrlList)
                            writtenToSubmit = True
                            modifiedQueryCount+=1


                if writtenToSubmit == False:
                    writeToSubmitFile(f_submit, currentSession, localUrlList)




            count+=1
    #closing the file handle
    f_submit.close()
    print "Modified %d test queries\n" % (modifiedQueryCount)
    print "Total number of queries %d\n" %(qcnt)



def main():
    """
    Read the file
    build up the dictionary for navigational queries
    [is that the best data structure to do it ? ]
    then start reading the test file
    update the dictionary we built previously alogn the way
    whenever a query has 'T' look to see if
    for that userID we have that queryTerm
    if so re-rank
    otherwise leave it as it is
    [maybe can experiment with some randomness]
    """

    #To avoid the problem of the garbage collector
    #complainging and stalling the program presumably
    #because the dict is consuming too much memory
    #read a thousand user-names of the dict
    #re-reank the personalizations from the test
    #set till we cross that userID
    # delete the dict and read a 1000 more

    # navigationalDict = {}
    # cnt = 0

    #file paths
    test_file = "../data/test"
    navig_file = "../data/navigationalQuery_dictionary_raw_form.txt"
    submit_file = "../data/submit_file"

    # f_test = open(test_file, "r")
    # f_navig = open(navig_file, "r")
    # f_submit = open(submit_file, "w")

    navigationalDict = loadNavigDict(navig_file)
    parseTest(test_file,submit_file, navigationalDict)
    # print navigationalDict[404]
    ## the garbage collection is fucked up
    ## takes a shit tonne of time.



    freeDict(navigationalDict)






if __name__ == '__main__':
    main()