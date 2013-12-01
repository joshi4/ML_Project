#!/usr/bin/env python

import scipy.sparse as sparse
NUM_LINES = 200000000#10000000
NUM_TEST_LINES = 3000000
NUM_USERS = 5736333 #taken from the kaggle website
NUM_DOMAINS = 5260184 #Placeholder value placed here.

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

def CreateDomainIndexMapping(totalDomains):
    """
    totalDomains --> set of all domains
    however, they are all random numbers
    going to assign each an index.
    """
    fout = open("../data/domainToIndexMapping", "w")
    fout.write("Index:DomainID\n")
    cnt = 0
    for ele in totalDomains:
        fout.write("%d:%d\n"%(cnt, ele))
    fout.close()


def ReadDomainIndexMapping(filename):
    domainToIndexMapping = {}
    with open(filename) as domain_index:
        for line in domain_index:
            line.strip('\n')
            tokens = line.split(':')
            index = int(tokens[0])
            domain = int(tokens[1])
            domainToIndexMapping[domain] = index
    return domainToIndexMapping





def createUserDomainVectors(train_path, totalDomains):
    currentUserID = -1
    currentSession = -1
    currentDomain = -1
    count = 0
    ##creating a sparse matrix
    #Rows = NUM_USERS
    #Columns/Features = NUM_DOMAINS
    userDomainMatrix = sparse.dok_matrix(NUM_USERS, NUM_DOMAINS)
    with open(train_path) as train:
        for line in train:
            count +=1
            if count % (NUM_LINES/10000) == 0 :
                print count
            if count > NUM_LINES:
                break
            line = line.strip('\n')
            tokens = line.split('\t')
            session = int(tokens[0])
            #inc count
            count+=1
            if(currentSession != session and currentSession >=0 ):
                #this means currentDomain at this point
                # was the final pick for the currentSession
                userVector[currentUserID][currentDomain]




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
    domainSet = CalcTotalDomains(test).union(CalcTotalDomains(train))
    CreateDomainIndexMapping(domainSet)
    print len(domainSet)
    # fout = open("../data/domain.info", "w")
    # fout.write("The domains in the training set are: %d\n" % (trainDomain) )
    # fout.write("The domains in the test set are: %d\n" % (testDomain))
    # fout.close()

if __name__ == '__main__':
    main()