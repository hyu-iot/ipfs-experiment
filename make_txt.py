

f = open("command.txt", 'w')

command_list = ["1 ls\n", "3 pwd\n", "2 ls -l\n"]
for i in range(len(command_list)):
    f.write(command_list[i])
f.close()

f = open("command.txt", 'r')
a = []
dic = {"id": [] , "command": []}

lines = f.readlines()
for line in lines:
    # a.append(line.split('\n')[0])
    dic["id"].append(line.split('\n')[0].split(" ")[0])
    dic["command"].append(line.split('\n')[0].split(" ")[1])
f.close()
print(a)
print(dic)
print(type(dic))