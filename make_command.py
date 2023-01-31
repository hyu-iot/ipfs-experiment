import sys

from itertools import *


n = int(sys.argv[1])
choice_n = int(sys.argv[2])
n_list = []
print(n)

for i in range(1,n+1):
    n_list.append(i)

sub_list = list(permutations(n_list, choice_n))
num = int(120/len(sub_list))
all_list = []
for j in range(num):
    for i in sub_list:
        all_list.append(i)
# all_list = list(permutations(n_list, choice_n))

print(len(all_list))
f = open("command.txt", 'w')
for i in range(len(all_list)):
    f.write(f"0 1 head -c 10000000 < /dev/urandom > test_file{i+1}\n")
    f.write(f"0 1 ipfs add test_file{i+1}\n")
    for j in all_list[i]:
        f.write(f"{j} 1 ipfs cat $1 > read_file{i+1}\n")
    f.write(f"{n+1} 1 ipfs cat $1 > read_file{i+1}\n")
f.close