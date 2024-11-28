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

# create database and tables
echo "CREATE DATABASE IF NOT EXISTS ${DB_NAME};" | mysql
echo "USE ${DB_NAME};" | mysql
echo "CREATE TABLE IF NOT EXISTS ${DB_NAME}.main_table (id INT AUTO_INCREMENT PRIMARY KEY, filename VARCHAR(255), deescription TEXT, source TEXT);" | mysql
# create user for pdv web client to allow it fetch data
echo "CREATE USER IF NOT EXISTS '${DB_USERNAME}'@'${WC_IPA}' IDENTIFIED BY '${DB_PASSWORD}';" | mysql
echo "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USERNAME}'@'${WC_IPA}';" | mysql
# create user for the pdv_host.py, currenly only one pdv host is supported
echo "CREATE USER IF NOT EXISTS 'pdvhost'@'192.168.1.18' IDENTIFIED BY 'Welcome@123';" | mysql
echo "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO 'pdvhost'@'192.168.1.18';" | mysql
