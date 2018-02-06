import sys
sys.setrecursionlimit(100000) 

list1 = [1,2,34,54,544,39,45,3,3,376]
count = len(list1)


def getmid(list1,low,hign):
    temp = list1[low]
    while low<hign:
        while low<hign and list1[hign] >= temp:
            hign = hign - 1
        list1[low] = list1[hign]
        while low<hign and list1[low] <= temp:
            low = low + 1
        list1[hign] = list1[low]
        list1[low] = temp;
        return low


def quiksort(list1,low,hign):
    if low<hign:
        mid = getmid(list1,low,hign)
        quiksort(list1,0,mid-1)
        quiksort(list1,mid+1,hign)

quiksort(list1,0,count-1)



for num in list1:
    print(num)
