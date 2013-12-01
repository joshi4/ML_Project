#!/usr/bin/env python

# import scipy.sparse as sparse
NUM_LINES = 200000000#10000000
NUM_TEST_LINES = 3000000
NUM_USERS = 5736333 #taken from the kaggle website
NUM_DOMAINS = 5260184 #Placeholder value placed here.
FINAL_CLICK_SCORE = 10000
def CalcTotalDomains(train):
    domains = set()
    cnt = 0
    with open(train) as f:
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
                    domains.add(int(pair[1]))
            cnt +=1
    return domains

# def CreateDomainIndexMapping(totalDomains):
    # """
    # totalDomains --> set of all domains
    # however, they are all random numbers
    # going to assign each an index.
    # """
    # fout = open("../data/domainToIndexMapping", "w")
    # fout.write("Index:DomainID\n")
    # cnt = 0
    # for ele in totalDomains:
        # fout.write("%d:%d\n"%(cnt, ele))
        # cnt+=1
    # fout.close()
#
# def ReadDomainIndexMapping(filename):
#     domainToIndexMapping = {}
#     with open(filename) as domain_index:
#         for line in domain_index:
#             line.strip('\n')
#             tokens = line.split(':')
#             index = int(tokens[0])
#             domain = int(tokens[1])
#             domainToIndexMapping[domain] = index
#     return domainToIndexMapping
#




## don't need any mapping; I thought hte domain
## id's were random but turns out they are not
## they are assigned from 0 to NUM_DOMAINS -1


def emptyDictionary(userVector,file_handle,uid):
    ###userID:domainName:score
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


def AddDwellTimes(userVector,currentDomain,currentUserID,score):
    if currentUserID in userVector:
        if currentDomain in userVector[currentUserID]:
            #update the value in the dict.
            #it means it was a final click

            #add a 1000 units
            score = userVector[currentUserID][currentDomain]
            score += score
        else :
            userVector[currentUserID][currentDomain] = score
    else:
        userVector[currentUserID] = {currentDomain: score}


def createUserDomainVectors(train_path):
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
    # userDomainMatrix = sparse.dok_matrix(NUM_USERS, NUM_DOMAINS)
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
                score = FINAL_CLICK_SCORE
                AddDwellTimes(userVector, currentDomain, currentUserID, score)

            currentSession = session
            #update the session value
            if (tokens[1] == "M"):
                currentUserID = int(tokens[3])
                ### FIX THIS BUG IN THE NAVIGATION AS WELL.
                ### will probably imporve my ranking.
                localUrlToDomainDict.clear()
            elif (tokens[2] == "Q" or tokens[2] == "T"):
                currentTime  = int(tokens[1])

                for i in range(6, len(tokens)):
                    pair = (tokens[i].split(','))
                    localUrlToDomainDict[int(pair[0])] = int(pair[1])

            elif (tokens[2] == "C"):
                if currentDomain != -1 :
                    #so that its not turtles all the way up
                    score = int(tokens[1]) - currentTime
                    AddDwellTimes(userVector,currentDomain,currentUserID,score)
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
    # test = "../data/test"
    # domainSet = CalcTotalDomains(test).union(CalcTotalDomains(train))
    # CreateDomainIndexMapping(domainSet)
    # print len(domainSet)
    # fout = open("../data/domain.info", "w")
    # fout.write("The domains in the training set are: %d\n" % (trainDomain) )
    # fout.write("The domains in the test set are: %d\n" % (testDomain))
    # fout.close()
    createUserDomainVectors(train)

if __name__ == '__main__':
    main()