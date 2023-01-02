# ipfs-experiment
IPFS experiment code file

It shows communication between 2 raspberri pi clients, 1 command_client, and 1 main server.

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
