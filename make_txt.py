

f = open("command.txt", 'w')

command_list = ["ls\n", "pwd\n", "ls -l\n"]
for i in range(len(command_list)):
    f.write(command_list[i])
f.close()

f = open("command.txt", 'r')
a = []

lines = f.readlines()
for line in lines:
    a.append(line.split('\n')[0])
    
f.close()

print(a)

print()