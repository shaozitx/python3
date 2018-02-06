list1 = [1,2,34,54,544,39,45,3,3,376]
count = len(list1)
for i in range(0,count):
	for j in range(i+1,count):
		if list1[i] > list1[j]:
			list1[i],list1[j] = list1[j] , list1[i]


for num in list1:
	print(num)