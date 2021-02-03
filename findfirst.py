def findFirst(inList):
    return next((i for i, x in enumerate(inList) if x), None)

if __name__ == "__main__":    
    inList = [0, 0, 0 , 0, 0, 0, 1, 0, 0, 1]
    print ("First non-zero index: {}".format(findFirst(inList)))
