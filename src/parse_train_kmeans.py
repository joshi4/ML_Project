#!/usr/bin/env python

import scipy.sparse as sp
NUM_LINES = 200000000#10000000
NUM_TEST_LINES = 3000000
NUM_USERS = 5736333 #taken from the kaggle website
NUM_DOMAINS =  5260184 #Placeholder value placed here.
# domain indices go from 0 to 5260183
FINAL_CLICK_SCORE = 10000
def CalcTotalDomains(listOfFiles):
    domains = set()
    domain_index = 0
    ### merging CreateIndexMapping in here
    ## to save time.
    fout = open("../data/domainToIndexMapping", "w")
    fout.write("Index:DomainID\n")
    for file_name in listOfFiles:
        cnt = 0
        with open(file_name) as f:
            for  line in  f:
                if cnt % (NUM_LINES/10000) == 0:
                    print cnt / (NUM_LINES/10000)
                if cnt > NUM_LINES:
                    break
                line = line.strip('\n')
                tokens = line.split('\t')
                if (tokens[2] == "Q" or tokens[2] == "T"):
                    for i in range(6, len(tokens)):
                        pair = tokens[i].split(',')
                        new_domain = int(pair[1])
                        if new_domain not in domains:
                            domains.add(new_domain)
                            fout.write("%d:%d\n"%(domain_index, new_domain))
                            domain_index +=1
                cnt+=1
    fout.close()
    return domains

# def CreateDomainIndexMapping(new_domain, f):
#     """
#     totalDomains --> set of all domains
#     however, they are all random numbers
#     going to assign each an index.
#     """
#     # fout = open("../data/domainToIndexMapping", "w")
#     fout.write("Index:DomainID\n")
#     # cnt = 0
#     # for ele in totalDomains:
#     fout.write("%d:%d\n"%(cnt, ele))
#     #     cnt+=1
#     # fout.close()
#
def ReadDomainIndexMapping():
    domainToIndexMapping = {}
    filename = "../data/domainToIndexMapping"
    flag = 0
    with open(filename) as domain_index:
        for line in domain_index:
            if flag == 0:
                flag = 1
                continue
            line.strip('\n')
                #avoid the first header line.
            tokens = line.split(':')
            index = int(tokens[0])
            domain = int(tokens[1])
            domainToIndexMapping[domain] = index
    return domainToIndexMapping
#



## don't need any mapping; I thought hte domain
## id's were random but turns out they are not
## they are assigned from 0 to NUM_DOMAINS -1

### fuckers are tricky there are very few
### select domains that are missing.


def emptyDictionary(userVector,file_handle,uid):
    ###userID:domainName:score ---> now instead of DomainName it will
    ## be domain name index.
    key_list = userVector.keys()
    for userId in key_list:
        if userId != uid:
            for domain in userVector[userId]:
                score = userVector[userId][domain]
                file_handle.write("%d:%d:%d\n"%(userId,domain,score))

    ##having written to file
    ## remove the keys
    for k in key_list:
        if k != uid:
            del userVector[k]


def AddDwellTimes(userVector,currentDomainIndex,currentUserID,score):
    if currentUserID in userVector:
        if currentDomainIndex in userVector[currentUserID]:
            #update the value in the dict.
            #it means it was a final click

            #add a 1000 units
            userVector[currentUserID][currentDomainIndex] += score
        else :
            userVector[currentUserID][currentDomainIndex] = score
    else:
        userVector[currentUserID] = {currentDomainIndex: score}


def createSparseMatrixOfFeatures(user_vector_path):
    userDomainMatrix = sp.dok_matrix((NUM_USERS, NUM_DOMAINS))
    # tmpCount = 0
    cnt = 0
    with open(user_vector_path) as fin:
        currentUserID = -1
        tmpDict = {}
        for line in fin:
            # tmpCount+=1
            # if tmpCount > 100:
            #     break
            line.strip('\n')
            tokens = [int(x) for x in line.split(':')]
            userID = tokens[0]
            domainIndex = tokens[1]
            score = tokens[2]

            if cnt % (NUM_LINES/10000) == 0:
                print cnt / (NUM_LINES/10000)

            cnt +=1
            if currentUserID != userID and currentUserID != -1:
                ## now add it to the sparse matrix
                ##delete the key
                for dom in tmpDict[currentUserID]:
                    print currentUserID,dom




                    userDomainMatrix[currentUserID,dom] = tmpDict[currentUserID][dom]


                    # if currentUserID == 5:
                    #     print dom,tmpDict[currentUserID][dom]

                del tmpDict[currentUserID]


            currentUserID = userID

            if currentUserID not in tmpDict:
                tmpDict[currentUserID] = {domainIndex:score}
            else:
                if domainIndex not in tmpDict[currentUserID]:
                    tmpDict[currentUserID][domainIndex] = score
                else:
                    tmpDict[currentUserID][domainIndex]+= score



    print userDomainMatrix.getrow(5).sum(axis=1)


def createUserDomainVectors(train_path, getIndexForDomain):
    currentUserID = -1
    currentSession = -1
    currentDomain = -1
    count = 0
    localUrlToDomainDict = {}
    ##creating a sparse matrix
    #Rows = NUM_USERS
    #Columns/Features = NUM_DOMAINS
    userVector = { }
    file_user_vector = open("../data/user-vector-hash", "w")
    clickFlag = False
    with open(train_path) as train:
        for line in train:
            if count % (NUM_LINES/10000) == 0 :
                print count / (NUM_LINES/10000)
            if count % (NUM_LINES/1000) == 0:
                emptyDictionary(userVector,file_user_vector, currentUserID)
            if count > NUM_LINES:
                emptyDictionary(userVector, file_user_vector, currentUserID)
                break
            count +=1
            line = line.strip('\n')
            tokens = line.split('\t')
            session = int(tokens[0])
            #inc count

            if(currentSession != session and currentSession >=0 ):
                #this means currentDomain at this point
                # was the final pick for the currentSession
                if clickFlag:
                    clickFlag = False
                    score = FINAL_CLICK_SCORE
                    AddDwellTimes(userVector, getIndexForDomain[currentDomain], currentUserID, score)

            currentSession = session
            #update the session value
            if (tokens[1] == "M"):
                clickFlag = False
                currentUserID = int(tokens[3])
                ### FIX THIS BUG IN THE NAVIGATION AS WELL.
                ### will probably imporve my ranking.
                localUrlToDomainDict.clear()
            elif (tokens[2] == "Q" or tokens[2] == "T"):
                clickFlag = False
                currentTime  = int(tokens[1])

                for i in range(6, len(tokens)):
                    pair = (tokens[i].split(','))
                    urlId = int(pair[0])
                    if urlId not in localUrlToDomainDict:
                        localUrlToDomainDict[urlId] = int(pair[1])

            elif (tokens[2] == "C"):
                clickFlag = True
                if currentDomain != -1 :
                    #so that its not turtles all the way up
                    score = int(tokens[1]) - currentTime
                    AddDwellTimes(userVector,getIndexForDomain[currentDomain],currentUserID,score)
                currentTime = int(tokens[1])
                currentDomain = localUrlToDomainDict[int(tokens[4])]



    file_user_vector.close()



def main():
    """
    userID's appear in sequential order
    create a vector for each user of
    domain ==> dwell time
    if its the last click add a certain max
    dwell time: say 1000

    First: need to find how many domains there are
    in the first place.

    prolly use a sparse array in scipy
    """

    train = "../data/train"
    test = "../data/test"
    user_vector_path = "../data/user-vector-hash"

    # domainSet = CalcTotalDomains(test).union(CalcTotalDomains(train))
    #domainSet = CalcTotalDomains([test,train])
    # CreateDomainIndexMapping(domainSet)
    #print len(domainSet), max(domainSet), min(domainSet) #5260184 5303713 0

    # fout = open("../data/domain.info", "w")
    # fout.write("The domains in the training set are: %d\n" % (trainDomain) )
    # fout.write("The domains in the test set are: %d\n" % (testDomain))
    # fout.close()

    # Get the domain index mapping

    getIndexForDomain = ReadDomainIndexMapping()
    createUserDomainVectors(train, getIndexForDomain) #; job is done

    #createSparseMatrixOfFeatures(user_vector_path)

if __name__ == '__main__':
    main()