#!/bin/bash

if [ -z $INSTALL_DIR ]; then
	INSTALL_DIR="/var"
fi
if [ -z $PORT ]; then
	echo "Port number is not specified using 400 as default"
	PORT = 400
fi
if [ -z $SERVICE_NAME ]; then
	SERVICE_NAME="pdvrunner"
fi


INSTALL_PATH="${INSTALL_DIR}/pdvrunner"

if [ -d $INSTALL_PATH ]; then
	echo "Error: ${INSTALL_PATH} already exists, please either remove it or specify INSTALL_DIR different from /var"
else
	echo "Creating directory ${INSTALL_PATH}"
	mkdir -p $INSTALL_PATH
	echo "Copying pdv_runner.py to ${INSTALL_PATH}"
	cp pdv_runner.py pdv.hpp $INSTALL_PATH
	echo "
[Unit]
Description=PDV Runner 1.0
After=network.target

[Service]
ExecStart=python ${INSTALL_PATH}/pdv_runner.py --port=${PORT}
Restart=always
WorkingDirectory=${INSTALL_PATH}

[Install]
WantedBy=multi-user.target
" 	> ${SERVICE_NAME}.service
	SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
	if [ -f $SERVICE_PATH ]; then
		echo "Error: Service /etc/systemd/system/${SERVICE_NAME} already exists, please either remove it or specify a different name using SERVICE_NAME variable"
	else
		cp ${SERVICE_NAME}.service $SERVICE_PATH
		systemctl start $SERVICE_NAME
		systemctl enable $SERVICE_NAME.service
		systemctl daemon-reload
		systemctl restart $SERVICE_NAME
	fi
fi
