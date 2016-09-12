from fabric.api import *
from fabric.contrib.files import exists
import os

HOMEDIR = os.environ['HOME']

with open(HOMEDIR + '/.ssh/id_rsa.pub', 'r') as sshpubkeyfile:
    SSHPUBKEY=sshpubkeyfile.read().replace('\n', '')

@task
def addCustomUser(customUser):
    run('adduser --disabled-password --gecos "" '+ customUser)

@task
def setupSSH4User(customUser):
    run("mkdir /home/" + customUser + "/.ssh")
    run("chmod 0700 /home/" + customUser + "/.ssh ")
    run("chown" + customUser + ":" + customUser + "/home/" + customUser + "/.ssh ")
    run("echo " + SSHPUBKEY + " >> home/" + customUser + "/.ssh/authorized_keys")
    run("chmod 0600 /home/" + customUser + "/.ssh/authorized_keys ")
    run("chown" + customUser + ":" + customUser + "/home/" + customUser + "/.ssh/authorized_keys ")



@task
def installRabbitMQ():
    sudo("apt-get update && apt-get -y upgrade")
    sudo('echo "deb http://www.rabbitmq.com/debian/ testing main" | tee -a /etc/apt/sources.list.d/rabbitmq.list')
    sudo("curl -L -o ~/rabbitmq-signing-key-public.asc http://www.rabbitmq.com/rabbitmq-signing-key-public.asc")
    sudo("apt-key add ~/rabbitmq-signing-key-public.asc")
    sudo("apt-get update && sudo apt-get -y upgrade")
    sudo("apt-get install -y rabbitmq-server erlang-nox")
    sudo("service rabbitmq-server start")
    run("cd /tmp && wget http://sensuapp.org/docs/0.13/tools/ssl_certs.tar && tar -xvf ssl_certs.tar")
    run("cd ssl_certs && ./ssl_certs.sh generate")
    sudo("mkdir -p /etc/rabbitmq/ssl && sudo cp /tmp/ssl_certs/sensu_ca/cacert.pem /tmp/ssl_certs/server/cert.pem /tmp/ssl_certs/server/key.pem /etc/rabbitmq/ssl")
    put("./rabbitmq.config", "/etc/rabbitmq/rabbitmq.config",use_sudo=True)
    sudo("service rabbitmq-server restart")
    sudo("rabbitmqctl add_vhost /sensu")
    sudo("rabbitmqctl add_user sensu QfP8myKrIS")
    sudo('rabbitmqctl set_permissions -p /sensu sensu ".*" ".*" ".*"')

@task
def installRedis():
    sudo("apt-get update && sudo apt-get -y upgrade")
    sudo("apt-get -y install redis-server")

@task
def installSensu():
    sudo("get -q http://repos.sensuapp.org/apt/pubkey.gpg -O- | sudo apt-key add -")
    sudo('echo "deb http://repos.sensuapp.org/apt sensu main" | sudo tee -a /etc/apt/sources.list.d/sensu.list')
    sudo('apt-get update &&  apt-get install -y sensu uchiwa')
    sudo('mkdir -p /etc/sensu/ssl')
    sudo('cp /tmp/ssl_certs/client/cert.pem /tmp/ssl_certs/client/key.pem /etc/sensu/ssl')

@task
def adduser(userid):
    sudo()

@task
def configureSensu():
    put("./rabbitmq.json", "/etc/sensu/conf.d/rabbitmq.json", use_sudo=True)
    put("./radis.json","/etc/sensu/conf.d/redis.json", use_sudo=True)
    put("./api.json", "/etc/sensu/conf.d/api.json", use_sudo=True)
    put("./uchiwa.json", "/etc/sensu/conf.d/uchiwa.json", use_sudo=True)
    put("./client.json", "/etc/sensu/conf.d/client.json", use_sudo=True)
    sudo("update-rc.d sensu-server defaults")
    sudo("update-rc.d sensu-client defaults")
    sudo("update-rc.d sensu-api defaults")
    sudo("update-rc.d uchiwa defaults")

@task
def startSensu():
    sudo("service sensu-server start")
    sudo("service sensu-client start")
    sudo("service sensu-api start")
    sudo("service uchiwa start")

@task
def stopSensu():
    sudo("service sensu-server stop")
    sudo("service sensu-client stop")
    sudo("service sensu-api stop")
    sudo("service uchiwa stop")

@task
def restartSensu():
    stopSensu()
    startSensu()
