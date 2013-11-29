#!/usr/bin/env python

NUM_NAVIG_LINES = 8500000

def freeDict(d):
    keys = d.keys()
    for k in keys:
        print "deleting: ", k
        del d[k]


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

    navigationalDict = {}
    cnt = 0

    #file paths
    # test_file = "../data/test"
    navig_file = "../data/navigationalQuery_dictionary_raw_form.txt"
    # submit_file = "../data/submit_file"

    # f_test = open(test_file, "r")
    # f_navig = open(navig_file, "r")
    # f_submit = open(submit_file, "w")

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
    print navigationalDict[404]
    freeDict(navigationalDict)






if __name__ == '__main__':
    main()