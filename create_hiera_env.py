#!/usr/bin/env python

from boto import vpc
import time
import os

# Making sure the env vars exist, so the script can run nicely. A bit dirty, but it's the only way I know!
KEY_NAME = os.getenv('KEY_NAME')
if KEY_NAME is None or KEY_NAME == '[ec2_keypair_name]':
    print("Error, KEY_NAME env var not found. Either KEY_NAME is not set in exportenv.sh, or exportenv.sh wasn't sourced. Edit exportenv.sh, make sure all vars are set, then run 'source exportenv.sh' or '. exportenv.sh'")
    exit()
KEY_FILE = os.getenv('KEY_FILE')
if KEY_FILE is None or KEY_FILE == '[ec2_private_key_file]':
    print("Error, KEY_FILE env var not found. Either KEY_FILE is not set in exportenv.sh, or exportenv.sh wasn't sourced. Edit exportenv.sh, make sure all vars are set, then run 'source exportenv.sh' or '. exportenv.sh'")
    exit()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
if AWS_ACCESS_KEY_ID is None or AWS_ACCESS_KEY_ID == '[string]' :
    print("Error, AWS_ACCESS_KEY_ID env var not found. Either AWS_ACCESS_KEY_ID is not set in exportenv.sh, or exportenv.sh wasn't sourced. Edit exportenv.sh, make sure all vars are set, then run 'source exportenv.sh' or '. exportenv.sh'")
    exit()
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
if AWS_SECRET_ACCESS_KEY is None or AWS_SECRET_ACCESS_KEY == '[string]':
    print("Error, AWS_SECRET_ACCESS_KEY env var not found. Either AWS_SECRET_ACCESS_KEY is not set in exportenv.sh, or exportenv.sh wasn't sourced. Edit exportenv.sh, make sure all vars are set, then run 'source exportenv.sh' or '. exportenv.sh'")
    exit()

# These are the AMI codes for Frankfurt (eu-central-1)
amazon='ami-d22932be'
ubuntu='ami-87564feb'
redhat='ami-875042eb'
nat   ='ami-17273c7b'

INSTANCE_TYPE  = 't2.micro'
IMAGE          = ubuntu # Basic 64-bit Ubuntu AMI
REGION         = 'eu-central-1' # If you change this, you'll need to change AMIs codes as well, as they're different for each region
PROJECT        = 'Hiera-demo'
SECURITY_GROUP = ['Hiera-demo']
PUPPET_NAME    = 'puppetmaster'
WEBSERVER1_PROD_NAME     = 'webserver1.us-east-1.prod.client1.com'
WEBSERVER2_PROD_NAME     = 'webserver2.us-east-1.prod.client1.com'
WEBSERVER1_PROD_DC2_NAME = 'webserver1.us-west-1.prod.client1.com'
WEBSERVER1_STAGE_NAME    = 'webserver1.us-west-1.stage.client1.com'
WEBSERVER1_DEV_NAME      = 'webserver1.us-east-1.dev.client1.com'
MYSQL1_PROD_NAME         = 'mysql1.us-east-1.prod.client1.com'
CLIENT2_NAME             = 'pweb1.client2.com'

PUPPET_NAME            = "puppetmaster"
PUPPET_USER_DATA       = """#!/bin/bash
# Installing puppet repo 
wget https://apt.puppetlabs.com/puppetlabs-release-trusty.deb -O /tmp/puppetlabs-release-trusty.deb 
dpkg -i /tmp/puppetlabs-release-trusty.deb

# Adding some lines to rc.local to run "apt-get update", "configure-pat.sh" and "set-hostname.sh" to be ran every time the server starts. And actually running all of it now.
sed -ie 's/^exit 0/apt-get update\\n# Configure PAT\\n\/usr\/local\/sbin\/configure-pat.sh\\n\/usr\/local\/sbin\/set-hostname.sh PUT_HERE_THE_SERVER_NAME\\nexit 0/g' /etc/rc.local
/etc/rc.local

# Enabling "noninteractive" so apt can install packages without questions
export DEBIAN_FRONTEND=noninteractive

# Upgrading all packages (takes a loooooong time, that's why it's commented out)
#apt-get dist-upgrade -y 

# Installing basic stuff
apt-get install -y joe puppet git puppetmaster whois

# Cloning github lab repo
git clone https://github.com/ersiko/puppet-hiera-lab.git 

# Copying puppet configuration
#cp -a puppet-hiera-lab/puppet-config/* /etc/puppet/.
cp -a /etc/puppet/* puppet-hiera-lab/puppet-config/.
mv /etc/puppet /etc/puppet.orig
ln -s /puppet-hiera-lab/puppet-config/ /etc/puppet

# Enabling puppet master start and cert autosigning
sed -i -e 's/START=no/START=yes/g' /etc/default/puppet
sed -i -e 's/\[master\]/\[master\]\\nautosign = true/g' /etc/puppet/puppet.conf 
sed -i -e 's/^templatedir=/#templatedir/g' /etc/puppet/puppet.conf 

# Copying configure-pat.sh and set-hostname.sh and setting them u+x
cp -a /puppet-hiera-lab/auxfiles/* /usr/local/sbin/.
chmod u+x /usr/local/sbin/set-hostname.sh  
chmod u+x /usr/local/sbin/configure-pat.sh  
mv /usr/local/sbin/52-labintro /etc/update-motd.d/
chmod u+x /etc/update-motd.d/52-labintro
cd /etc/puppet;git checkout 0-StartFromScratch

# Setting the server name in hostname and /etc/hosts
echo PUT_HERE_THE_SERVER_NAME > /etc/hostname
echo PUT_HERE_THE_PUPPET_MASTER_IP PUT_HERE_THE_PUPPET_MASTER_NAME >> /etc/hosts

# Linking /etc/hiera.yaml to /etc/puppet/hiera.yaml
rm /etc/hiera.yaml
ln -s /etc/puppet/hiera.yaml /etc/hiera.yaml

# Adding hiera config to puppet
echo "hiera_include('classes')" >> /etc/puppet/manifests/site.pp 

# Make puppet data owned by puppet
chown -R puppet /etc/puppet/data 

# Set aliases for the different steps in the lab
echo "alias 0='cd /etc/puppet;git checkout 0-StartFromScratch;cat /usr/local/sbin/0-StartFromScratch;service puppetmaster restart'" >> /root/.bashrc
echo "alias 1='cd /etc/puppet;git checkout 1-Common;cat /usr/local/sbin/1-CommonPackages;service puppetmaster restart;puppet module install puppetlabs-ntp'" >> /root/.bashrc
echo "alias 2='cd /etc/puppet;git checkout 2-EnvVars;cat /usr/local/sbin/2-EnvVars;service puppetmaster restart;puppet module install ghoneycutt-ssh'" >> /root/.bashrc
echo "alias 3='cd /etc/puppet;git checkout 3-DCVars;cat /usr/local/sbin/3-DCVars;service puppetmaster restart'" >> /root/.bashrc
echo "alias 4='cd /etc/puppet;git checkout 4-RoleVars;cat /usr/local/sbin/4-RoleVars;service puppetmaster restart;puppet module install puppetlabs-apache;puppet module install puppetlabs-mysql'" >> /root/.bashrc
echo "alias 5='cd /etc/puppet;git checkout 5-HostVars;cat /usr/local/sbin/5-HostVars;service puppetmaster restart'" >> /root/.bashrc
echo "alias 6='cd /etc/puppet;git checkout 6-EnvAndRoleVars;cat /usr/local/sbin/6-EnvAndRoleVars;service puppetmaster restart'" >> /root/.bashrc
echo "alias 7='cd /etc/puppet;git checkout 7-MixDCandEnvsAndRoles;cat /usr/local/sbin/7-MixDCandEnvsAndRoles;service puppetmaster restart'" >> /root/.bashrc
echo "alias 8='cd /etc/puppet;git checkout 8-ClientVars;cat /usr/local/sbin/8-ClientVars;service puppetmaster restart;puppet module install nodes-php'" >> /root/.bashrc

# And wrapping all up with a reboot
reboot
"""


WEBSERVER_NAME            = "webserver"
WEBSERVER_USER_DATA       = """#!/bin/bash

# Setting the server name in hostname and /etc/hosts
echo PUT_HERE_THE_SERVER_NAME  > /etc/hostname
echo PUT_HERE_THE_PUPPET_MASTER_IP PUT_HERE_THE_PUPPET_MASTER_NAME >> /etc/hosts


# Adding some lines to rc.local to run "apt-get update" and "set-hostname.sh" to be ran every time the server starts. And actually running all of it now.
sed -ie 's/^exit 0/apt-get update\\n\/usr\/local\/sbin\/set-hostname.sh PUT_HERE_THE_SERVER_NAME\\nexit 0/g' /etc/rc.local
/etc/rc.local


# Enabling "noninteractive" so apt can install packages without questions
export DEBIAN_FRONTEND=noninteractive

# Puppetmaster will reboot eventually, and that may break this installation. We don't want that to happen
while [ ! -e /etc/puppet/puppet.conf ];do 
    # Downloading the "set-hostname.sh" script && \\ 
    wget https://raw.githubusercontent.com/ersiko/puppet-hiera-lab/master/auxfiles/set-hostname.sh -O /usr/local/sbin/set-hostname.sh && \\
    chmod u+x /usr/local/sbin/set-hostname.sh && \\
    # Installing puppet repo  && \\ 
    wget https://apt.puppetlabs.com/puppetlabs-release-trusty.deb -O /tmp/puppetlabs-release-trusty.deb && \\ 
    dpkg -i /tmp/puppetlabs-release-trusty.deb && \\ 
    /etc/rc.local && \\ 
    # Upgrading all packages (takes a loooooong time, that's why it's commented out) && \\ 
    #apt-get dist-upgrade -y && \\ 
    # Installing basic stuff && \\ 
    apt-get install -y joe puppet git
done 

# Configuring puppet, setting query interval to 30 seconds, and setting the puppet master server name and then making puppet start at boot
sed -i -e 's/\[main\]/\[main\]\\nserver=PUT_HERE_THE_PUPPET_MASTER_NAME\\nruninterval=30/g' /etc/puppet/puppet.conf
sed -i -e 's/START=no/START=yes/g' /etc/default/puppet
sed -i -e 's/^templatedir=/#templatedir/g' /etc/puppet/puppet.conf 

# And wrapping all up with a reboot
reboot
"""



def launch_instance(VPC_CON,INS_NAME,INS_USER_DATA,INS_IMAGE=IMAGE,INS_TYPE=INSTANCE_TYPE,INS_KEY_NAME=KEY_NAME,INS_SECGROUPS=[],INS_SUBNET="",INS_PROJECT=PROJECT,PUPPET_MASTER_IP='127.0.0.1'):
    SERVER_NAME = INS_NAME 
    USER_DATA_SERVERNAME = INS_USER_DATA.replace("PUT_HERE_THE_SERVER_NAME", SERVER_NAME) #I'm not proud of this dirty trick I frequently use on my bash scripting, but it's handy. Sorry!
    USER_DATA_SERVERNAME = USER_DATA_SERVERNAME.replace("PUT_HERE_THE_PUPPET_MASTER_IP", PUPPET_MASTER_IP) # Ditto
    USER_DATA_SERVERNAME = USER_DATA_SERVERNAME.replace("PUT_HERE_THE_PUPPET_MASTER_NAME", PUPPET_NAME + '.' + REGION + '.compute.internal') # Ditto
    USER_DATA_SERVERNAME = USER_DATA_SERVERNAME.replace("PUT_HERE_THE_BE_SUBNET", subnetbe.cidr_block)
    #print("Creating " + SERVER_NAME + " with user_data " + USER_DATA_SERVERNAME)
    reservation = VPC_CON.run_instances(image_id          =INS_IMAGE, 
                                        instance_type     =INS_TYPE, 
                                        key_name          =INS_KEY_NAME, 
                                        security_group_ids=INS_SECGROUPS, 
                                        user_data         =USER_DATA_SERVERNAME,
                                        subnet_id         =INS_SUBNET.id)
    time.sleep(3)
    instance=reservation.instances[0]
    instance.add_tag("Project", INS_PROJECT)
    instance.add_tag("Name", SERVER_NAME)
    return instance



print("Connecting to AWS")
vpc_con = vpc.connect_to_region(REGION)
print("Creating VPC")
my_vpc  = vpc_con.create_vpc('10.0.0.0/16')
vpc_con.modify_vpc_attribute(my_vpc.id, enable_dns_support=True)
vpc_con.modify_vpc_attribute(my_vpc.id, enable_dns_hostnames=True)
print("Tagging VPC")
my_vpc.add_tag("Name",PROJECT+"-VPC")
my_vpc.add_tag("Project",PROJECT)
print("Creating subnets")
subnetdmz  = vpc_con.create_subnet(my_vpc.id,'10.0.1.0/24')
subnetbe   = vpc_con.create_subnet(my_vpc.id,'10.0.2.0/24')
print("Tagging subnet")
subnetdmz.add_tag("Name",PROJECT+"-Subnet")
subnetdmz.add_tag("Project",PROJECT)
subnetbe.add_tag("Name",PROJECT+"-Subnet")
subnetbe.add_tag("Project",PROJECT)
print("Creating internet gateway")
gateway = vpc_con.create_internet_gateway()
gateway.add_tag("Project",PROJECT)
print("Attaching gateway to VPC")
vpc_con.attach_internet_gateway(gateway.id, my_vpc.id)
print("Creating route table")
route_table = vpc_con.create_route_table(my_vpc.id)
route_table.add_tag("Project",PROJECT)
print("Associating route table to subnet")
vpc_con.associate_route_table(route_table.id, subnetdmz.id)
print("Create route to the internet")
route = vpc_con.create_route(route_table.id, '0.0.0.0/0', gateway.id)
print("Creating Security group")
secgroup = vpc_con.create_security_group(PROJECT+'_group','A security_group for' + PROJECT, my_vpc.id)
print("Opening port 22 and other stuff in the secgroup ")
secgroup.authorize(ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
secgroup.authorize(ip_protocol='tcp', from_port=0, to_port=65535, cidr_ip='10.0.0.0/16')
secgroup.authorize(ip_protocol='icmp', from_port=-1, to_port=-1, cidr_ip='10.0.0.0/16')
secgroup.add_tag("Project",PROJECT)

print("Creating puppetmaster instance in VPC")
puppetmaster=launch_instance(VPC_CON=vpc_con,
                             INS_NAME=PUPPET_NAME, 
                             INS_USER_DATA=PUPPET_USER_DATA,
                             INS_SECGROUPS=[secgroup.id],
                             INS_SUBNET=subnetdmz)

while puppetmaster.update() != "running":
    time.sleep(5)
    print ("Waiting for puppetmaster to start")

print("Setting puppetmaster as NAT for private subnet")
vpc_con.modify_instance_attribute(puppetmaster.id,'sourceDestCheck',False)
default_route_table = vpc_con.get_all_route_tables(filters=({'vpc-id': my_vpc.id, 'association.main': 'true'}))
default_route_table[0].add_tag("Project",PROJECT)
natroute = vpc_con.create_route(default_route_table[0].id, '0.0.0.0/0', instance_id=puppetmaster.id)

print("Creating dev webserver node instance(s) in VPC")
dev=launch_instance(VPC_CON=vpc_con,
                    INS_NAME=WEBSERVER1_DEV_NAME,
                    INS_USER_DATA=WEBSERVER_USER_DATA,
                    INS_SECGROUPS=[secgroup.id],
                    INS_SUBNET=subnetbe,
                    PUPPET_MASTER_IP=puppetmaster.private_ip_address)

print("Creating stage webserver node instance(s) in VPC")
stage=launch_instance(VPC_CON=vpc_con,
                    INS_NAME=WEBSERVER1_STAGE_NAME,
                    INS_USER_DATA=WEBSERVER_USER_DATA,
                    INS_SECGROUPS=[secgroup.id],
                    INS_SUBNET=subnetbe,
                    PUPPET_MASTER_IP=puppetmaster.private_ip_address)

print("Creating prod1 webserver node instance(s) in VPC")
prod1=launch_instance(VPC_CON=vpc_con,
                    INS_NAME=WEBSERVER1_PROD_NAME,
                    INS_USER_DATA=WEBSERVER_USER_DATA,
                    INS_SECGROUPS=[secgroup.id],
                    INS_SUBNET=subnetbe,
                    PUPPET_MASTER_IP=puppetmaster.private_ip_address)

print("Creating prod2 webserver node instance(s) in VPC")
prod2=launch_instance(VPC_CON=vpc_con,
                    INS_NAME=WEBSERVER2_PROD_NAME,
                    INS_USER_DATA=WEBSERVER_USER_DATA,
                    INS_SECGROUPS=[secgroup.id],
                    INS_SUBNET=subnetbe,
                    PUPPET_MASTER_IP=puppetmaster.private_ip_address)


print("Creating prod1dc2 webserver node instance(s) in VPC")
prod1dc2=launch_instance(VPC_CON=vpc_con,
                    INS_NAME=WEBSERVER1_PROD_DC2_NAME,
                    INS_USER_DATA=WEBSERVER_USER_DATA,
                    INS_SECGROUPS=[secgroup.id],
                    INS_SUBNET=subnetbe,
                    PUPPET_MASTER_IP=puppetmaster.private_ip_address)

print("Creating prodmysql webserver node instance(s) in VPC")
mysql1=launch_instance(VPC_CON=vpc_con,
                    INS_NAME=MYSQL1_PROD_NAME,
                    INS_USER_DATA=WEBSERVER_USER_DATA,
                    INS_SECGROUPS=[secgroup.id],
                    INS_SUBNET=subnetbe,
                    PUPPET_MASTER_IP=puppetmaster.private_ip_address)

print("Creating client2 webserver node instance(s) in VPC")
client2=launch_instance(VPC_CON=vpc_con,
                    INS_NAME=CLIENT2_NAME,
                    INS_USER_DATA=WEBSERVER_USER_DATA,
                    INS_SECGROUPS=[secgroup.id],
                    INS_SUBNET=subnetbe,
                    PUPPET_MASTER_IP=puppetmaster.private_ip_address)


print("Creating elasticip")
elasticip = vpc_con.allocate_address(domain='vpc')
print("Associating elasticip to puppetmaster instance")
vpc_con.associate_address(instance_id=puppetmaster.id, allocation_id=elasticip.allocation_id)

print("**********************************************************************")
print("**                     Env created successfully                     **")
print("**********************************************************************")
print("")
print("Now you should be able to connect to the servers copy/pasting the following lines:")
print("")
print("Puppetmaster: ")
print("ssh ubuntu@" + elasticip.public_ip + " -o \"StrictHostKeyChecking no\" -i " + KEY_FILE + 
                                            " -L 2222:" + dev.private_ip_address + ":22 -L 8082:" + dev.private_ip_address + ":80 " +
                                            " -L 2223:" + stage.private_ip_address + ":22 -L 8083:" + stage.private_ip_address + ":80 " +
                                            " -L 2224:" + prod1.private_ip_address + ":22 -L 8084:" + prod1.private_ip_address + ":80 " +
                                            " -L 2225:" + prod2.private_ip_address + ":22 -L 8085:" + prod2.private_ip_address + ":80 " +
                                            " -L 2226:" + prod1dc2.private_ip_address + ":22 -L 8086:" + prod1dc2.private_ip_address + ":80 " +
                                            " -L 2227:" + mysql1.private_ip_address + ":22 "
                                            " -L 2228:" + client2.private_ip_address + ":22 -L 8088:" + client2.private_ip_address + ":80 " +
                                            ";ssh-keygen -f ~/.ssh/known_hosts -R "+ elasticip.public_ip)
print("Dev:")
print("ssh-keygen -f ~/.ssh/known_hosts -R [localhost]:2222;ssh -o \"StrictHostKeyChecking no\" ubuntu@localhost -p 2222 -i " + KEY_FILE)
print("Stage:")
print("ssh-keygen -f ~/.ssh/known_hosts -R [localhost]:2223;ssh -o \"StrictHostKeyChecking no\" ubuntu@localhost -p 2223 -i " + KEY_FILE)
print("Prod1:")
print("ssh-keygen -f ~/.ssh/known_hosts -R [localhost]:2224;ssh -o \"StrictHostKeyChecking no\" ubuntu@localhost -p 2224 -i " + KEY_FILE)
print("Prod2: ")
print("ssh-keygen -f ~/.ssh/known_hosts -R [localhost]:2225;ssh -o \"StrictHostKeyChecking no\" ubuntu@localhost -p 2225 -i " + KEY_FILE)
print("Prod1 at dc2:") 
print("ssh-keygen -f ~/.ssh/known_hosts -R [localhost]:2226;ssh -o \"StrictHostKeyChecking no\" ubuntu@localhost -p 2226 -i " + KEY_FILE)
print("Mysql1:")
print("ssh-keygen -f ~/.ssh/known_hosts -R [localhost]:2227;ssh -o \"StrictHostKeyChecking no\" ubuntu@localhost -p 2227 -i " + KEY_FILE)
print("Client2:")
print("ssh-keygen -f ~/.ssh/known_hosts -R [localhost]:2228;ssh -o \"StrictHostKeyChecking no\" ubuntu@localhost -p 2227 -i " + KEY_FILE)


