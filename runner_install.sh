#!/bin/bash

if [ -z $INSTALL_DIR ]; then
	INSTALL_DIR="/var"
fi
if [ -z $PORT ]; then
	echo "Port number is not specified using 400 as default"
	PORT=400
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
	echo "Copying pdv_runner.py pdv.hpp to ${INSTALL_PATH}"
	cp pdv_runner.py pdv.hpp $INSTALL_PATH
	if [[ "$OSTYPE" == "linux-gnu"* ]]; then
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
" 		> ${SERVICE_NAME}.service
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
	elif [[ "$OSTYPE" == "freebsd"* ]]; then
		echo "
#!/bin/sh

# PROVIDE: ${SERVICE_NAME}
# REQUIRE: netif
# BEFORE:

. /etc/rc.subr

name=\"${SERVICE_NAME}\"
desc=\"PDV Runner 1.0\"
rcvar=\"${SERVICE_NAME}_enable\"
pdvrunner_script=\"${INSTALL_DIR}/pdvrunner/pdv_runner.py\"
pdvrunner_args=\"--port ${PORT} --cpp_compiler=$(which g++) --c_compiler=$(which gcc) --include_dir=${INSTALL_DIR}/pdvrunner\"
pdvrunner_log=\"${INSTALL_DIR}/pdvrunner/pdv_runner.log.txt\"
daemon_exec=$(which daemon)
daemon_opt=\"-r\"
python_exec=$(which python)
cat_exec=$(which cat)

load_rc_config \"\$name\" :\${${SERVICE_NAME}_enable=\"NO\"}

start_cmd=\"${SERVICE_NAME}_start\"
stop_cmd=\"${SERVICE_NAME}_stop\"
status_cmd=\"${SERVICE_NAME}_status\"

${SERVICE_NAME}_start()
{
	echo \"pdvrunner is starting\"
	\${python_exec} \${pdvrunner_script} \${pdvrunner_args} &
}

${SERVICE_NAME}_stop()
{
	echo \"pdvrunner is stopping\"
}

${SERVICE_NAME}_status()
{
	\${cat_exec} ${pdvrunner_log}
}

run_rc_command \"\$1\"
" > ${SERVICE_NAME}
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"
		SERVICE_PATH=/etc/rc.d/${SERVICE_NAME}
		if [ -f $SERVICE_PATH ]; then
			echo "Error: Service ${SERVICE_PATH} already exists, please either remove it or specify a different name using SERVICE_NAME variable"
		else
			cp ${SERVICE_NAME} $SERVICE_PATH
			chmod +x $SERVICE_PATH
			sysrc ${SERVICE_NAME}_enable="YES"
			service ${SERVICE_NAME} start
		fi
	else
		echo "Can't recognized the OSType, currently only linux and freebsd are supported"
		exit 1
	fi
	
fi
