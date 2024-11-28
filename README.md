# PDV
A tool to automate running C++ snippets of algorithms and data structures on different CPUs, collect performance data, and display them on a webpage.

Why can't we use Github/Gitlab Runners and CI/CD? It's because it is a bit complex to achieve "Process just commited (pushed) file only".

## Dependency/Package Requirements
### For PDV Runners
#### On Linux (Ubuntu)
```
sudo pip install argparse
sudo pip install netifaces
sudo apt install lscpu
```
#### On FreeBSD (13.2)
In super user mode
```
pkg install python311
pkg install py311-pip
pip install netifces
pkg install lscpu
```
### For PDV Host
#### For Linux (Ubuntu)
```
sudo pip install argparse
sudo pip install netifaces
sudo pip install icmplib
sudo pip install mysqlclient
```
#### For FreeBSD (13.2)
In super user mode
```
pkg install python311
pkg install py311-pip
pip install icmplib
pip install mysqlclient
```

## Overview
There are three components which together make PDV work
### PDV Host (pdv_host.py)
This is the main script which manages everything and is supposed to be run everytime you want to run tests and upload data to the database.
It should be run like the following:
```
$ sudo python pdv_host.py --port 400 --db_server="192.168.1.18" --db_passwd="abcd" --file main.cpp  --title “Linked List v/s Vector Test” --description "This experiment demonstrates performance of vector vs linked list"
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

## Getting Started (Installing)
### Setting up PDV Web Client server (Machine1)
You'll need .net framework in Ubuntu, and execute `install.sh` bash script in sudo mode. This script builds the blazor web app, prepares the systemd service file, and installs into the /etc/systemd/system directory.

The following parameters need to be specified while executing the script:
- `URL`: This the url on which you would like to access the web client app
- `DB_NAME`: The database name in mysql (more in mysql database section)
- `DB_USERNAME`: Username registered in the mysql data which the web app uses to read data from the database 'DB_NAME'
- `DB_PASSWORD`: Password for DB_USERNAME
- `DB_SERVER`: IP address of the mysql server (more in mysql database section)
```
sudo apt install -y dotnet-sdk-8.0
git clone https://github.com/ravi688/PDV
cd PDV
chmod +x ./install.sh
sudo URL="http://192.168.1.15:80" DB_NAME="db_pdv" DB_USERNAME="pdvwebclient" DB_PASSWORD="1234" DB_SERVER="192.168.1.18" ./install.sh
```
### Setting up Mysql Database server (Machine2)
You'll need to install mysql-server in Ubuntu or any other linux distro and execute `./db_setup.sh` bash script in sudo mode. This script creates a database 'db_pdv', a table 'db_pdv.main_table' and creates users.

NOTE: You may also configure the file at `/etc/mysql/mysql.conf.d/mysqld.cnf` to bind mysql's server socket to a different ip address (must of some NIC on the same computer) other than 127.0.0.1 (default one).

The following parameters need to be specified while executing the script:
- `WC_IPA`: IP address of the web client server you just setup in the previou section
- `DB_NAME`: The database name in which pdv_host.py will store data to
- `DB_USERNAME`: Username for the web client in mysql database to allow web client access the database
- `DB_SERVER`: IP address of this machine, the mysql server
```
sudo apt-get install mysql-server
git clone https//github.com/ravi688/PDV
sudo WC_IPA="192.168.1.15" DB_NAME="db_pdv" DB_USERNAME="pdvwebclient" DB_PASSWORD="1234" DB_SERVER="192.168.1.18" PDV_HOST_IPA="192.168.1.22" PDV_HOST_PSWD="abcd" ./db_setup.sh
```
### Setting up PDV Runners (Machine3)
You'll need to install dependency packages mentioned in the very first section, clone the repo and run `pdv_runner.py` script in python.
The following parameters need to be specified:
 - `--port`: The port number at which to listen, this must be the same as what is specified while running `pdv_host.py` script
```
git clone https://github.com/ravi688/PDV
sudo python pdv_runner.py --port 400
```
To install the script as service, do the following:
```
chmod +x ./runner_install.sh
sudo PORT=400 ./runner_install.sh
```
### Setting up PDV Host and making first commit (Machine4)
You'll need to install dependency packages mentioned in the very first section, clone the repo and run `pdv_host.py` script in python.
The following parameters need to be specified:
 - `--port`: Port number of pdv runners, it must match with ones specified while running pdv_runner.py
 - '--db_server': IP address of the database server
 - '--db_passwd': Password of the 'pdvhost' user, this must match with 
 - `--ipa_file`: (optional) This file contains list of key value pairs ("dummy names of runner machines", "their ip adress")
 - `--file`: Path to the C and C++ source file which need to be commited
 - `--title`: Title of the experiment
 - `--description`: (optional) Description of the expriment, if not specified then, 'nano' text editor will popup to let you enter the description
```
git clone https://github.com/ravi688/PDV
sudo python pdv_host.py --port 400 --db_server="192.168.1.18" --db_passwd="abcd" --ipa_file pdv_clients.json --file main.cpp --title "Parallel Merge Sort --description "This experiment shows parallel merge sort in C++"
```
The contents of the pdv_clients.json file should be like as follows:
```
{
	"Intel Core i5 12400" : "192.168.1.19",
	"AMD Ryzen 5 5600G" : "192.168.1.20",
	"Intel Core i3 10100F" : "192.168.1.15",
	"Intel Core i5 8350U" : "192.168.1.18"
}
```

## Desktop Client (Optional)
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
- [x] Rename pdv_client.py to pdv_runner.py and associated strings in python scripts
- [ ] Release version 1.0 of PDV with self-contained PDVWebClient tarball, pdv_runner.py, pdv_host.py, and Database setup script or schema
- [ ] Test multiple times in byhyve virtual machines and docker to make things are working without issues
- [ ] Add time stamps for each entry registered in the mysql database
- [ ] The result.xml file should also specify the exact command used to compile the source files - which will help reproduce the same results
