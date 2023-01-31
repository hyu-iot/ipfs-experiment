import os
import time

# stream = os.popen('cd ../../.ipfs/blocks/;rm -rf *')
# time.sleep(1)
# stream = os.popen('cp -p SHARDING ../../.ipfs/blocks/')
# time.sleep(1)
stream = os.popen('rm -rf read*')
time.sleep(1)
stream = os.popen('rm -rf test*')

