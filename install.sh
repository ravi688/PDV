#!/bin/bash

if [ -z $INSTALL_DIR ]; then
	INSTALL_DIR="/var"
fi
if [ -z $URL ]; then
	URL="http://local_host:5094"
fi
if [ -z $DB_SERVER ]; then
	DB_SERVER="local_host"
fi
if [ -z $DB_USERNAME ]; then
	DB_USERNAME="pdvwebclient"
fi
if [ -z $DB_PASSWORD ]; then
	DB_PASSWORD="12345"
fi
if [ -z $DB_NAME ]; then
	DB_NAME="db_pdv"
fi
if [ -z $SERVICE_NAME ]; then
	SERVICE_NAME="pdvwebclient"
fi

INSTALL_PATH="${INSTALL_DIR}/pdvwebclient"

BUILD_DIR="PDVWebClient.build.dir"

dotnet publish -c Release --self-contained -r linux-x64 PDVWebClient/ -o $BUILD_DIR

if [ -d $INSTALL_PATH ]; then
	echo "Error: ${INSTALL_PATH} already exists, please either remove it or specify INSTALL_DIR different from /var"
else
	echo "Creating directory ${INSTALL_PATH}"
	mkdir -p $INSTALL_PATH
	echo "Copying all files to ${INSTALL_PATH}"
	cp -r $BUILD_DIR/* $INSTALL_PATH
	echo "
[Unit]
Description=PDV Web Client 1.0
After=network.target

[Service]
ExecStart=${INSTALL_PATH}/PDVWebClient --urls=\"${URL}\" --databaseServer=\"${DB_SERVER}\" --databaseName=\"${DB_NAME}\" --databaseUser=\"${DB_USERNAME}\" --dbUserPassword=\"${DB_PASSWORD}\"
Restart=always
WorkingDirectory=${INSTALL_PATH}

[Install]
WantedBy=multi-user.target
" 	> pdvwebclient.service
	SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
	if [ -f $SERVICE_PATH ]; then
		echo "Error: Service /etc/systemd/system/pdvwebclient already exists, please either remove it or specify a different name using SERVICE_NAME variable"
	else
		cp pdvwebclient.service $SERVICE_PATH
		systemctl start pdvwebclient
		systemctl enable pdvwebclient
		systemctl daemon-reload
		systemctl restart pdvwebclient
	fi
fi
