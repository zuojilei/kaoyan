

# sum=0
# for i in range(1,5,1):
#     for j in range(1,5,1):
#         for k in range(1,5,1):
#             if(i!=j&j!=k):
#                 sum=sum+1
#                 print (i,j,k ) # 这里去重
# print (sum)

a = ((1,'b'),(2,'c'),(3,'a'))
# print(a)
# item = {}
# for x in range(3):
#     alist = list(map(lambda x :x[1],filter(lambda x:x[0]==x,a)))
#     print(alist)
#     if alist:
#         item[x] = alist
# print(item)

item = {}
for i in a:
    item[i[0]] = (item.get(i[0]) if item.get(i[0]) else []) + [i]
print(item)