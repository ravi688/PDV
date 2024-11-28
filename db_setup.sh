#!/bin/bash

if [ -z $WC_IPA ]; then
	WC_IPA="local_host"
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
if [ -z $PDV_HOST_IPA ]; then
	PDV_HOST_IPA="127.0.0.1"
fi

# create database and tables
echo "CREATE DATABASE IF NOT EXISTS ${DB_NAME};" | mysql
echo "USE ${DB_NAME};" | mysql
echo "CREATE TABLE IF NOT EXISTS ${DB_NAME}.main_table (id INT AUTO_INCREMENT PRIMARY KEY, filename VARCHAR(255), title VARCHAR(255), description TEXT, source TEXT);" | mysql
# create user for pdv web client to allow it fetch data
echo "CREATE USER IF NOT EXISTS '${DB_USERNAME}'@'${WC_IPA}' IDENTIFIED BY '${DB_PASSWORD}';" | mysql
echo "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USERNAME}'@'${WC_IPA}';" | mysql
# create user for the pdv_host.py, currenly only one pdv host is supported
echo "CREATE USER IF NOT EXISTS 'pdvhost'@'${PDV_HOST_IPA}' IDENTIFIED BY 'Welcome@123';" | mysql
echo "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO 'pdvhost'@'${PDV_HOST_IPA}';" | mysql
