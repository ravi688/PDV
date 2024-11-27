# PDV
A tool to automate running C++ snippets of algorithms and data structures on different CPUs, collect performance data, and display them on a webpage.

Why can't we use Github/Gitlab Runners and CI/CD? It's because it is a bit complex to achieve "Process just commited (pushed) file only".

## Package Requirements
### On Linux (Ubuntu)
```
sudo pip install icmplib
sudo pip install argparse
sudo pip install netifaces
sudo pip install mysqlclient
sudo apt install lscpu
```
### On FreeBSD (13.2)
In super user mode
```
pkg install python311
pkg install py311-pip
pip install netifces
pip install icmplib
pip install mysqlclient
pkg install lscpu
```

## Overview
There are three components which together make PDV work
### PDV Host (pdv_host.py)
This is the main script which manages everything and is supposed to be run everytime you want to run tests and upload data to the database.
It should be run like the following:
```
$ sudo python pdv_host.py --port 400 --file main.cpp  --message “Linked List v/s Vector Test”
Searching for PDV runners….
Found 2 runners
1. Core i5 12400
2. Ryzen 5 5600G
Sending source…
Waiting for results…
Got from Core i5 1200
Got from Ryzen 5 5600G
Uploading results to Database server…
Done!
```
### PDV Runner (pdv_runner.py)
This script should be installed in all the nodes participating in running the source snippets and should be launched once (be kept running).
It listens for PDV Host for source snippets, and compiles the them, builds executable, runs them and sends the result back to PDV Host.
It should be run like the following:
```
$ sudo python pdv_runner.py --port 400
Waiting for source…
Got source <main.cpp>
g++ -std=c++20 -lpdv -I$(pkg-config pdv –flags) <main.cpp> -o ./main
Sending result to pdv host…
Done!
```
### Bash script to setup Database and WebPage (webpage_db_setup.sh)
This script only need to be run once to setup webpage and database.
It should be run like the following:
```
$ ./webpage_db_setup.sh <port number>
```

### Desktop Client (Optional)
The source snippets would generate large number of key-value pairs with keys being tuple of inputs and value being tuple of outputs. This data needs to be displayed in an elegant graphical way, which is done by Desktop Client software (based on [SGE](https://github.com/ravi688/VulkanRenderer)).
This client software fetches data from the database and plots them on the screen in 3D or 2D, based on the type of data.
Additionally, it can also perform gradient descend to select the most suitable algorithm or data structure and input values!

### TODO
- [x] Refactor the pdv_host.py to first fetch ip addreses of all the NICs on the host device and then search for pdv clients
- [x] If --ipa_file has non-null value, then use this as a .json file to parse it and get the ip addresses of pdv clients from there only
- [x] After ack, send the file supplied via --file argument to pdv clients, that should be as soon as a pdv client is found
- [ ] Maintain a pdv clients status register in pdv_host, pdv_host would instantiate threads to listen for status updates for each pdv client
- [ ] Once pdv host has sent the file to all the found pdv clients, it must wait on every pdv client to finish, if any pdv client reports errorneous status then display it but let others finish
- [x] Create a standalone C (C++ compatible) header file to provide set of minimal and easy to use functions to generate an .xml file containing performance metrics data
- [x] In pdv_client.py, it should invoke gcc (if file received has .c extension) or g++ (it has .cpp extension) to compile the source into an executable and run it to generate .xml file
- [x] After .xml file is generated, it should be send back to pdv host as response
- [x] On pdv host side, it would receive .xml files from all the pdv clients (if success), and add entries to the centralized database by parsing the xml file.
- [x] PDV web client would fetch the tables from the centralized database and render visual table in the browser
- [ ] Rename pdv_client.py to pdv_runner.py and associated strings in python scripts
- [ ] Release version 1.0 of PDV with self-contained PDVWebClient tarball, pdv_runner.py, pdv_host.py, and Database setup script or schema
- [ ] Test multiple times in byhyve virtual machines and docker to make things are working without issues
- [ ] Add time stamps for each entry registered in the mysql database
- [ ] The result.xml file should also specify the exact command used to compile the source files - which will help reproduce the same results
