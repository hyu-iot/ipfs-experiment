import pandas as pd

# data = {'id' : [ '1', '2', '3'],
#         'ip_address' : [ "127.0.0.1", "127.0.0.1", "127.0.0.1"],
#         }

data = {'id' : [ '1'],
        'ip_address' : [ "127.0.0.1"],
        }


df = pd.DataFrame(data)

df.to_csv("info.csv")

