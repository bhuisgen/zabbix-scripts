#
# Fabric tasks for Zabbix 
#
# Boris HUISGEN <bhuisgen@>
#

from fabric.api import *
from fabric.utils import *

import ConfigParser
import os

env.colorize_errors = True
env.roledefs = {
    # role: ['host1', 'host2']
}

local_path = os.getcwd()
remote_path = "/home/%s/fabric" % (env.user)

#
# TASKS
#

@task
def start():
	"""
	start zabbix agent
	"""	
	sudo("/etc/init.d/zabbix-agent start")

@task
def stop():
	"""
	stop zabbix agent
	"""
	sudo("/etc/init.d/zabbix-agent stop")

@task
def restart():
	"""
	restart zabbix agent
	"""
	sudo("/etc/init.d/zabbix-agent restart")

@task
def install():
	"""
	install zabbix agent
	"""
	sudo("apt-get install zabbix-agent")

@task
def configure(file="./config.ini"):
	"""
	configure zabbix agent

	file: configuration file to read (default: ./config.ini)
	"""
	config = ConfigParser.RawConfigParser()
	config.read(file)

	if config.get("Agent", "LogFile") == "syslog":
		sudo("sed -i '/^LogFile\=.*/d' /etc/zabbix/zabbix_agentd.conf")
	else:
		sudo("sed -i 's/^LogFile\=.*/LogFile\=%s/' /etc/zabbix/zabbix_agentd.conf" % (config.get("Agent", "LogFile")))

	sudo("sed -i 's/^Server\=.*/Server\=%s/' /etc/zabbix/zabbix_agentd.conf" % (config.get("Agent", "Server")))
	sudo("sed -i 's/^ServerActive\=.*/ServerActive\=%s/' /etc/zabbix/zabbix_agentd.conf" % (config.get("Agent", "ServerActive")))
	sudo("sed -i 's/^Hostname\=.*/Hostname\=%s/' /etc/zabbix/zabbix_agentd.conf" % (env.host_string))
	sudo("sed -i 's/^StartAgents\=.*/StartAgents\=%s/' /etc/zabbix/zabbix_agentd.conf" % (config.get("Agent", "StartAgents")))
	sudo("sed -i 's/^Include\=.*/Include\=%s/' /etc/zabbix/zabbix_agentd.conf" % (config.get("Agent", "Include").replace("/", "\/")))

	with warn_only():
		sudo("mv /etc/zabbix/zabbix_agentd.d/ /etc/zabbix/zabbix_agentd.conf.d/")

	sudo("/etc/init.d/zabbix-agent stop")

	with warn_only():
		sudo("mkdir /var/lib/zabbix")
	sudo("chmod 700 /var/lib/zabbix")
	sudo("chown zabbix:zabbix /var/lib/zabbix")
	sudo("usermod -d /var/lib/zabbix zabbix")
	sudo("usermod -a -G adm,nslcd,clamav zabbix")
	sudo("/etc/init.d/zabbix-agent start")

	with warn_only():
		sudo("rm /etc/cron.daily/tripwire")
		sudo("sed -i 's/^MAIL-ON-WARNING\=.*$/MAIL-ON-WARNING\=\"\"/' /etc/rkhunter.conf")
		sudo("sed -i 's/^RUN_DAILY\=.*$/RUN_DAILY\=\"false\"/' /etc/chkrootkit.conf")

@task
def deploy():
	"""
	deploy scripts files
	"""
	run("mkdir -p %s/zabbix" % (remote_path))

	put("%s/zabbix" % (local_path), "%s" % (remote_path), mirror_local_mode=True)
	sudo("rsync -a %s/zabbix/scripts/ /etc/zabbix/scripts/" % (remote_path))
	sudo("rsync -a %s/zabbix/zabbix_agentd.conf.d/ /etc/zabbix/zabbix_agentd.conf.d/" % (remote_path))

	sudo("chown -R root:zabbix /etc/zabbix/scripts")
	sudo("chmod -R o-rwx /etc/zabbix/scripts")
	sudo("chown -R root:zabbix /etc/zabbix/zabbix_agentd.conf.d")
	sudo("chmod -R o-rwx /etc/zabbix/zabbix_agentd.conf.d")

	sudo("/etc/init.d/zabbix-agent restart")

	run("rm -fr %s/zabbix" % (remote_path))

@task
def trapper(name):
	"""
	run trapper script
	"""
	sudo("su -s /bin/bash -c \"/etc/zabbix/scripts/trapper/%s\" zabbix" % (name))
