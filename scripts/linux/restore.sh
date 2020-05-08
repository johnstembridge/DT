#!/bin/sh
sudo service mysql stop
mysql -e "drop database dt"
mysql -e "create database dt character set utf8 collate utf8_bin"
mysql dt < /var/data/backups/dt-db_new.sql
sudo service mysql start