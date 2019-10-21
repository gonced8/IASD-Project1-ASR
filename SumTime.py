#!/usr/local/bin/python3

def sumtime(t1, t2):
    # Receives two time strings and returns one string of the summed time
    sumtime = [int(t1[2*i:2*(i+1)]) + int(t2[2*i:2*(i+1)]) for i in range(2)]
    if sumtime[1] >= 60: # More than 60 minutes
        sumtime[0] += 1
        sumtime[1] -= 60
    return "{:02d}{:02d}".format(sumtime[0], sumtime[1])
    # Returns string with added zeros if necessary, format hhmm


if (__name__ == "__main__"):
    # Example
    t1 = '0830'
    t2 = '1240'
    print(sumtime(t1,t2))
