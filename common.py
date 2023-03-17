
import csv
import pandas as pd
from ast import literal_eval

hello_rc = 0
hello_cc = 1

def str2sec(x):
    h, m, s = x.strip().split(':') 
    return float(h)*3600 + float(m)*60 + float(s) #int() 

def make_csv(dic):
    with open('result_1.csv', 'w', newline='') as csvfile:
        fieldnames = ['client_id','command', 'result']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(len(dic['command'])):
            client_id_0 = dic["client_id"][i]
            command = dic['command'][i]
            result_0 = dic['result'][i]
            # print(client_id, command, result_0)
            writer.writerow({'client_id': client_id_0, 'command': command, 'result': result_0})
    kr_ = pd.read_csv("result_1.csv", converters={"result": literal_eval})
    kr_["Duration of Time"] = ''
    kr_["Timestamp"] = 0
    kr_["Duration of Time(sec)"] = ''
    for i,j in enumerate(kr_["command"]):
        if j[:8] == "ipfs add":
            kr_["Duration of Time"][i] = kr_["result"][i][1]
            kr_["Timestamp"][i] = kr_["result"][i][2]
            kr_["Duration of Time(sec)"][i] = str2sec(kr_["result"][i][1])
            kr_["result"][i] = kr_["result"][i][0]
        elif j == "Timeout expired":
            kr_["Duration of Time"][i] = None
            kr_["Timestamp"][i] = None
            kr_["Duration of Time(sec)"][i] = None
            kr_["result"][i] = None
        else:
            kr_["Duration of Time"][i] = kr_["result"][i][0]
            kr_["Timestamp"][i] = kr_["result"][i][1]
            kr_["Duration of Time(sec)"][i] = str2sec(kr_["result"][i][0])
            kr_["result"][i] = None
    kr_.columns.values[2] = "Hash value"
    kr_.to_csv('result_1.csv',index=False)
   
total_result_list = {"client_id" : [], "command":[], "result": []}

f = open('result_1_1.csv', 'r')
lines = f.readlines()
print(f)
print(lines[1])
print(len(lines))
for n,line in enumerate(lines):
    if n == 0:
        continue
    total_result_list["client_id"].append(line.split(",",maxsplit=2)[0])
    total_result_list["command"].append(line.split(",",maxsplit=2)[1])
    x = literal_eval(line.split(",",maxsplit=2)[2])
    print(type(x))
    total_result_list["result"].append(literal_eval(line.split(",",maxsplit=2)[2]))
print(type(total_result_list["result"][0]))
print(total_result_list["result"][0])

# print(total_result_list)
make_csv(total_result_list)