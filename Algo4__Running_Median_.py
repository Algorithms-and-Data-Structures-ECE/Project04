import numpy as np
import time


######################### Global Variables #########################
#my seed
np.random.seed(1063199)

MAX_POSITION = 1000
MAX_TEMP = 50
TEMP_DECIMALS = 2
NUMBER_OF_SPOTS = 500000
NUMBER_OF_SPOTS_IN_ARRAY = 100


######################### Functions #########################
#random values for a spot
def createSpot():
    x = np.random.randint(0, MAX_POSITION)
    y = np.random.randint(0, MAX_POSITION)
    key = str(x)+str(y)
    temp = MAX_TEMP * np.random.random()
    temp = round(temp, TEMP_DECIMALS)
    return key, temp

#make the heaps have the same size +-1
def rebalanceHeaps(below_median_heap, above_median_heap):
    if below_median_heap.size > above_median_heap.size + 1:
        key,temp = below_median_heap.extractMin()
        #in the below_median_heap we store the temp with the opposite sign 
        #in order to use it as a max heap
        temp = -temp
        spot = Spot(key, temp)
        above_median_heap.insert(spot)

    elif above_median_heap.size > below_median_heap.size + 1:
        key,temp = above_median_heap.extractMin()
        temp = -temp
        spot = Spot(key, temp)
        below_median_heap.insert(spot)

#the below_median_heap should have a lower max value than the min of above_median_heap
def fixHeapValues(below_median_heap, above_median_heap):
    while -below_median_heap.getMin()[1] > above_median_heap.getMin()[1]:
        #get the top spots from the heap
        old_below_key,old_below_temp = below_median_heap.extractMin()
        #in the below_median_heap we store the temp with the opposite sign 
        #in order to use it as a max heap
        old_below_temp = -old_below_temp
        old_below_spot = Spot(old_below_key, old_below_temp)

        old_above_key,old_above_temp = above_median_heap.extractMin()
        #in the below_median_heap we store the temp with the opposite sign 
        #in order to use it as a max heap
        old_above_temp = -old_above_temp
        old_above_spot = Spot(old_above_key, old_above_temp)

        #switch the spots
        below_median_heap.insert(old_above_spot)
        above_median_heap.insert(old_below_spot)


def calculateMedian(below_median_heap, above_median_heap):
    #if both heaps are empty there is no median
    if below_median_heap.size == 0 and above_median_heap.size == 0:
        return None

    #if a heap has 1 more element then the median is at the top of the heap
    #be careful with values from the below_median_heap
    elif below_median_heap.size == above_median_heap.size + 1:
        return -below_median_heap.getMin()[1]

    elif above_median_heap.size == below_median_heap.size + 1:
        return above_median_heap.getMin()[1]

    #if both heaps have the same number of elements then calculate the average
    else:
        median = (-below_median_heap.getMin()[1] + above_median_heap.getMin()[1])/2
        #round to 2 decimals
        median = round(median, TEMP_DECIMALS)
        return median

def updateExistingSpots(below_median_heap, above_median_heap):
    #check if we already have the spot in order to update it
    if above_median_heap.isInMinHeap(spot.key):
        index = above_median_heap.pos[str(spot.key)]
        if spot.temp > above_median_heap.array[index][1]:
            above_median_heap.increaseTemp(spot.key, spot.temp)
        else:
            above_median_heap.decreaseTemp(spot.key, spot.temp)
        
        fixHeapValues(below_median_heap, above_median_heap)
        return True

    elif below_median_heap.isInMinHeap(spot.key):
        #dont forget to adjust the temp
        spot.temp = - spot.temp
        index = below_median_heap.pos[str(spot.key)]
        if spot.temp > below_median_heap.array[index][1]:
            below_median_heap.increaseTemp(spot.key, spot.temp)
        else:
            below_median_heap.decreaseTemp(spot.key, spot.temp)

        fixHeapValues(below_median_heap, above_median_heap)
        return True

    return False

######################### Classes #########################
#class to store the spot info
class Spot:
    def __init__(self, key, temp):
        self.key = key
        self.temp = temp


class MinHeap():
    def __init__(self, spots):
        # tuple (key, value)
        self.array = []    
        # position of key in array
        self.pos = {}         
        # elements in min heap
        self.size = len(spots)      

        #add all the elements of the list to heap
        for i, item in enumerate(spots):
            self.array.append((spots[i].key, spots[i].temp))
            self.pos[spots[i].key] = i

        #sort the elements into a heap
        for i in range(self.size // 2, -1, -1):
            self.heapify(i)

    # display items of heap
    def display(self):
        print('Array:', end=' ')
        for i in range(self.size):
            print(f'({self.array[i][0]} : {self.array[i][1]})', end=' ')
        print()


    # modify array so that i roots a heap, down-heap
    def heapify(self, i):
        #assume that this elements is the smallest
        smallest = i
        #get the children
        le = 2 * i + 1
        ri = 2 * i + 2

        #check if the left child is smaller
        if le < self.size and self.array[le][1] < self.array[smallest][1]:
            smallest = le
        #check if the right child is smaller
        if ri < self.size and self.array[ri][1] < self.array[smallest][1]:
            smallest = ri

        #if the smallest element is not the initial change positions and call recursively
        if smallest != i:
            # update pos
            self.pos[self.array[smallest][0]] = i
            self.pos[self.array[i][0]] = smallest
            # swap
            self.array[smallest], self.array[i] = self.array[i], self.array[smallest]
            self.heapify(smallest)

    #check if heap is empty
    def isEmpty(self):
        return self.size == 0

    # return the min element of the heap (it is always the top element)
    def getMin(self):
        if self.size == 0:
            return None
        return self.array[0]

    # return and remove the min element of the heap
    def extractMin(self):
        #if heap is empty do nothing
        if self.size == 0:
            return None

        #if it has elements then we need to remove the top element
        root = self.array[0]
        lastNode = self.array[self.size - 1]
        self.array[0] = lastNode
        #update pos
        self.pos[lastNode[0]] = 0
        del self.pos[root[0]]
        self.size -= 1
        self.heapify(0)
        return root

    # decreace value of item (key, value)
    def decreaseTemp(self, key, new_temp):
        i = self.pos[key]

        # new value must be smaller than current
        if self.array[i][1] <= new_temp:
            return

        self.array[i] = (key, new_temp)
        # check if is smaller than parent
        p = (i - 1) // 2
        while i > 0 and self.array[i][1] < self.array[p][1]:
            # update pos
            self.pos[self.array[i][0]] = p
            self.pos[self.array[p][0]] = i
            # swap
            self.array[p], self.array[i] = self.array[i], self.array[p]
            i = p
            p = (i - 1) // 2

    # increace value of item (key, value)
    def increaseTemp(self, key, new_temp):
        i = self.pos[key]
        # new value must be greater than current
        if self.array[i][1] >= new_temp:
            return
        self.array[i] = (key, new_temp)
        # check children
        self.heapify(i)

    # insert item (key, value)
    def insert(self, spot):
        # insert an item at the end with big value
        if self.size < len(self.array):
            self.array[self.size] = (spot.key, 10**80)
        else:
            self.array.append((spot.key, 10**80))

        self.pos[spot.key] = self.size
        self.size += 1
        self.decreaseTemp(spot.key, spot.temp)

    def isInMinHeap(self, key):
        key = str(key)
        if key in self.pos:
            if self.pos[key] <= self.size:
                return True

        return False


######################### Main #########################
start_time = time.time()
#start by adding 1 spot for each heap
key, temp = createSpot()
spot = Spot(key, temp)
above_median_heap = MinHeap([spot])
#save to the array
spots = [spot]

#in the below_median_heap we store the temp with the opposite sign 
#in order to use it as a max heap
key, temp = createSpot()
spot = Spot(key, -temp)
below_median_heap = MinHeap([spot])
#save to the array
spots.append(spot)

#fix the values so that the min of above_median_heap is bigger than the max below_median_heap
fixHeapValues(below_median_heap, above_median_heap)
"""
print("Above Median Heap")
above_median_heap.display()
print("Below Median Heap")
below_median_heap.display()
"""
#start keeping track of the median
median = calculateMedian(below_median_heap, above_median_heap)
#print("Median: ", median, "\n")

#-2 because we create 2 spots before the loop
for i in range(NUMBER_OF_SPOTS-2):
    #create a spot
    key, temp = createSpot()
    spot = Spot(key, temp)

    #save NUMBER_OF_SPOTS_IN_ARRAY in an array to use them to change their temp
    if i < NUMBER_OF_SPOTS_IN_ARRAY - 2:
        spots.append(spot)

    if(updateExistingSpots(below_median_heap, above_median_heap)):
        pass

    #if we dont have that key add it to the correct heap
    elif spot.temp >= median:
        above_median_heap.insert(spot)
    else:
        spot.temp = - spot.temp
        below_median_heap.insert(spot)

    #rebalance and fix the heaps if needed
    rebalanceHeaps(below_median_heap, above_median_heap)
    fixHeapValues(below_median_heap, above_median_heap)
    #calculate the median again
    median = calculateMedian(below_median_heap, above_median_heap)

end_time_all_passes = time.time()
time1 = end_time_all_passes - start_time
print("Total time for ", NUMBER_OF_SPOTS, "number of passes is ", time1)

"""
print("Above Median Heap")
above_median_heap.display()
print("Below Median Heap")
below_median_heap.display()
print("Median: ", median, "\n")
"""

for i in range(0, len(spots)):
    #get a random temperature
    spot.temp = MAX_TEMP * np.random.random()
    spot.temp = round(spot.temp, TEMP_DECIMALS)
    updateExistingSpots(below_median_heap, above_median_heap)
    median = calculateMedian(below_median_heap, above_median_heap)
        
end_time = time.time()
total_time = end_time - start_time
print("Total time for the whole program is ", total_time)

"""
print("Above Median Heap")
above_median_heap.display()
print("Below Median Heap")
below_median_heap.display()
print("Median: ", median, "\n")
"""