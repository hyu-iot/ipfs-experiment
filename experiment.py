


f = open("command.txt", 'r')
a = []
dic = {"id": [] , "command": []}
lines = f.readlines()
for line in lines:
    line_v = line.strip()
    if line_v[0] == '#':
        continue
    dic["id"].append(line_v.split('\n')[0].split(" ")[0])
    dic["command"].append(line_v.split('\n')[0].split(" ")[1])
f.close()
print(dic)
print(type(dic))