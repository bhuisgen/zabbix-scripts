# Scripts and templates for Zabbix

Boris HUISGEN <bhuisgen@hbis.fr>

## Description

This package contains zabbix scripts and templates :

* *config/zabbix_agentd.conf*: default agent configuration file
* *templates/*: all templates to import in zabbix frontend
* *zabbix/scripts*: all item scripts
* *zabbix/scripts/discovery* : all discovery scripts
* *zabbix/scripts/trapper* : all trapper scripts

## Installation

    # apt-get install fabric

## Configuration

    # cp config.init.dist config.ini

    # vim config.ini

## Fabric tasks

### Install

To install the agent :

	# fab -H host1,host2 install

    # fab -R role install

### Configure

To configure the agent :

	# fab -H  host1,host2 configure

    # fab -R role configure

This task will replace common configuration settings from the values found in file *config.ini* :

	[Agent]
	LogFile = syslog # set to syslog to remove LogFile option and enable syslog
	Server = 80.81.82.83
	ServerActive = 80.81.82.83
	StartAgents = 1
	Include = /etc/zabbix/zabbix_agentd.conf.d/

The task creates a home directory to user *zabbix* and add it to secondary groups to allow system logs and files reading :

    # mkdir /var/lib/zabbix
    # chown zabbix:zabbix /var/lib/zabbix
    # usermod -d /var/lib/zabbix zabbix
    # usermod -a -G adm,nslcd,clamav zabbix

You need to allow *sudo* for *zabbix* user (this it not done by the configure task) :

	# vim /etc/sudoers.d/zabbix

	zabbix    ALL=(ALL:ALL) NOPASSWD: /bin/netstat,/sbin/iptables,/usr/bin/aptitude               # Linux Debian
	zabbix    ALL=(ALL:ALL) NOPASSWD: /usr/sbin/chkrootkit,/usr/bin/rkhunter,/usr/sbin/tripwire   # Security programs
	zabbix    ALL=(ALL:ALL) NOPASSWD: /usr/sbin/smartctl                                          # SMART disks
	zabbix    ALL=(ALL:ALL) NOPASSWD: /usr/sbin/mpt-status                                        # MegaRAID controllers
	zabbix    ALL=(ALL:ALL) NOPASSWD: /usr/sbin/drbd-overview                                     # DRBD disks
	zabbix    ALL=(ALL:ALL) NOPASSWD: /etc/zabbix/scripts/diff                                    # Diff check
	zabbix    ALL=(ALL:ALL) NOPASSWD: /etc/zabbix/scripts/backup                                  # Backup check

### Deployment

To deploy/update all scripts :

	# fab -H host1 deploy

### Execute a trapper script

    # fab -H host1 trapper:name

## Templates and scripts

### Aptitude

	# crontab  -l -u zabbix

	0 6 * * * /bin/sh /etc/zabbix/scripts/trapper/aptitude

### Backup

	# vim /etc/zabbix/scripts/trapper/backup.conf

	# vim /etc/zabbix/scripts/trapper/backup

	# crontab  -l -u zabbix

	0 6 * * * /bin/sh /etc/zabbix/scripts/trapper/backup

### Chkrootkit

	# crontab  -l -u zabbix

	0 6 * * * /bin/sh /etc/zabbix/scripts/trapper/chkrootkit

### Diff

	# vim /etc/zabbix/scripts/trapper/diff.conf
	# vim /etc/zabbix/scripts/trapper/diff.files

	# vim /etc/zabbix/scripts/trapper/diff

	DIFF_FILES=/etc/zabbix/scripts/trapper/diff.files
	DIFF_SERVERS=srv-beta-wp1

	# crontab  -l -u root

	0 * * * * /bin/sh /etc/zabbix/scripts/trapper/diff

### Elasticsearch

	# crontab -l -u zabbix

	*/5 * * * * /bin/sh /etc/zabbix/scripts/trapper/elasticsearch

### MySQL

	# mysql -u root -p

	mysql> GRANT SELECT,PROCESS,SUPER ON *.* TO 'zabbix'@'localhost' IDENTIFIED BY 'secret';
	mysql> FLUSH PRIVILEGES

	# vim /var/lib/zabbix/.my.cnf

	[client]
	socket=/var/run/mysqld/mysqld.sock
	user=zabbix
	password=secret

	# chown zabbix:zabbix /var/lib/zabbix/.my.cnf
	# chmod 600 /var/lib/zabbix/.my.cnf

	# crontab -l -u zabbix

	*/1 * * * * /bin/sh /etc/zabbix/scripts/trapper/mysql
	*/5 * * * * /bin/sh /etc/zabbix/scripts/trapper/mysql-databases
	*/15 * * * * /bin/sh /etc/zabbix/scripts/trapper/mysql-tables

### Nginx

	# cat /etc/nginx/sites-enabled/status

	server {
	   listen 127.0.0.1:80 default_server;
	   listen 192.168.0.1:80 default_server;
	   listen 127.0.0.1:443 ssl;
	   listen 192.168.0.1:443 ssl;

	   ssl_certificate /etc/nginx/ssl/server.crt;
	   ssl_certificate_key /etc/nginx/ssl/server.key;

	   root /usr/share/nginx/html;
	 
	   location /nginx_status {
	      stub_status on;
	      access_log off;
	      allow 127.0.0.1;
	      deny all;
	   }
	}

To allow extern HTTP/HTTPS check, add this virtual host :

	server {
	   listen <PUBLIC_IP>:80;
	   listen <PUBLIC_IP>:443 ssl;

	   server_name localhost;
	   ssl_certificate     /etc/nginx/ssl/localhost.crt;
	   ssl_certificate_key /etc/nginx/ssl/localhost.key;
	}

### PHP
	
	# vi /etc/php5/fpm/pool.d/beta.conf

	[beta]
	user = www-data
	group = www-data

	listen = /var/run/php5-$pool.sock

	listen.owner = www-data
	listen.group = www-data
	listen.mode = 0600

	pm.status_path = /php_status-$pool
	ping.path = /php_ping-$pool
	;ping.response = pong
 
	# cat /etc/nginx/sites-enabled/status

	server {
	   listen 127.0.0.1:80;
	 
	   server_name localhost;
	   root /usr/share/nginx/html;
	 
	   location ~ ^/(php_(ping|status))-(.+)$ {
	      set $pool $3;
	 
	      include fastcgi_params;
	      fastcgi_pass unix:/var/run/php5-$pool.sock;
	      fastcgi_param SCRIPT_FILENAME $fastcgi_script_name;
	      allow 127.0.0.1;
	      deny all;
	   }
	 
	   location ~ ^/(phpinfo|apc|php_apc)-(.+)(\.php?)$ {
	      set $script $1;
	      set $pool $2;
	 
	      include fastcgi_params;
	      fastcgi_pass unix:/var/run/php5-$pool.sock;
	      fastcgi_param SCRIPT_FILENAME $document_root/$script.php;
	      allow 127.0.0.1;
	      deny all;
	   }
	}

	# ls -l /usr/share/nginx/html/

	total 64
	-rw-r--r-- 1 root root   537 Mar  4 12:46 50x.html
	-rw-r--r-- 1 root root 46105 May  2 16:08 apc.php
	-rw-r--r-- 1 root root   612 Mar  4 12:46 index.html
	-rw-r--r-- 1 root root   600 May  2 17:23 php_apc.php
	-rw-r--r-- 1 root root    25 May  2 15:43 phpinfo.php

### PostgreSQL

	# vim /etc/postgresql/9.1/main/postgresql.conf

	log_destination = 'syslog'

	# su postgres
	$ createuser -D -S -W zabbix
	$ exit

	# su -s /bin/bash zabbix
	$ cat /var/lib/zabbix/.pgpass
	 
	localhost:5432:*:zabbix:pa$$word

	# chown 600 /var/lib/zabbix/.pgpass

	# vim /etc/postgresql/9.1/main/pg_hba.conf
	 
	host     all             zabbix         127.0.0.1/32         md5

	# crontab -l -u zabbix

	*/1 * * * * /bin/sh /etc/zabbix/scripts/trapper/pgsql
	*/5 * * * * /bin/sh /etc/zabbix/scripts/trapper/pgsql-databases
	*/15 * * * * /bin/sh /etc/zabbix/scripts/trapper/pgsql-tables

### Redis

	# vim /etc/redis/redis.conf

	unixsocket /var/run/redis/redis.sock
	unixsocketperm 775

	# usermod -a -G redis zabbix

	# crontab -l -u zabbix

	*/1 * * * * /bin/sh /etc/zabbix/scripts/trapper/redis
	*/1 * * * * /bin/sh /etc/zabbix/scripts/trapper/redis-databases

### Rkhunter

	# crontab  -l -u zabbix
	 
	0 6 * * * /bin/sh /etc/zabbix/scripts/trapper/rkhunter

### Tripwire

	# crontab  -l -u zabbix
	 
	0 6 * * * /bin/sh /etc/zabbix/scripts/trapper/tripwire
