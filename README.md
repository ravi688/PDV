# PDV
A tool to automate running C++ snippets of algorithms and data structures on different CPUs, collect performance data, and display them on a webpage.

## Overview
There are three components which together make PDV work
### PDV Host (pdv_host.py)
This is the main script which manages everything and is supposed to be run everytime you want to run tests and upload data to the database.
It should be run like the following:
```
$ python pdv_host.py <main.cpp> “Linked List v/s Vector Test”
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
$ python pdv_runner.py
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
