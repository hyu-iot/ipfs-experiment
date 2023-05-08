# ipfs-experiment
IPFS experiment code file

It shows communication between 2 raspberri pi clients, 1 command_client, and 1 main server.

- Script Setting
  - basic script file is command.txt
  - A B C (A is node's order. B is option number where 0 is parallel and 1 is sequential. C is command line.
  - 'head -c 1024 < /dev/urandom > test_file1' is generating 1024 Bytes file as test_file1.
  - 'ipfs add test_file1' is uploading the test_file1 in IPFS environment.
  - 'ipfs cat $1 > read_file1' is downloading the file from other nodes connecting in IPFS environment.

## Testing
- Environment setting
  - We need total 4 terminals to implement testing
  - We need to install some packages in raspberry pi environment
    - pip3 install pandas
    - sudo apt-get install libatlas-base-dev
    - pip3 install os
    - pip3 install psutil

- Implement
  - python3 Main_server.py
  - python3 rc_0.py info.csv
  - python3 rc_1.py info.csv
  - python3 Comm_client.py info.csv command.txt
  
- Result
  - If you do 'Ctrl-C' Comm_client.py, terminal is terminated and generates the csv file including the command, timestamp, and results.
  
- Reset
  - reset.py is the file that removes the files in .ipfs/blocks in order to reduce the embedded device's capacity and adds the SHARDING file because IPFS needs the file in .ipfs/blocks.
