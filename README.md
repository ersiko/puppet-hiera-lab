# "How does puppet work with hiera?" lab
Lab for the puppet-hiera presentation
This lab blablabla

## What is an ENC (external node classifier)?

## Requirements for this lab
Install python and boto

## Preparation
Create servers or run the script

## Confirming the env is working
puppet cert --list --all

## First step: Configuring hiera and installing packages common to all servers
In this step we'll set hiera to apply the modules that will be common to all the servers in our infrastructure. In our case, that will be the "ntp" package.

In the puppet master, logged as root, type "1" (just a plain number one) and it will checkout the proper git branch with the puppet configuration.

Relevant files:
 - `/etc/puppet/hiera.yaml`: 
 In this file we're describing where hiera should look for config files with classes and variables to apply to the servers in our infrastructure, and the precedence of them. More details in [the hiera.xml section in puppet docs](https://docs.puppetlabs.com/hiera/3.0/configuring.html). 

 - `/etc/puppet/data/common.yaml`: 
 We set this path is the previous hiera.yaml file. Classes and variables on this file will be applied to all servers. 

 Shortly after this (30 seconds max) you should see in all the servers `/var/log/syslog` how "ntp" package is installed. Also `apt-cache policy ntp` will show it.

## Second step: Configuring variables depending on the environment
Access to prod servers is usually restricted to just a few people, while access to dev environments is more broad. We can manage access with hiera, depending on the env of the server.

To continue, in the puppet master, logged as root, type "2" (just a plain number two) and it will checkout the proper git branch with the puppet configuration.

First of all, we'll install an ssh puppet module by running "puppet module install ghoneycutt-ssh" as root (the "2" command will run this command for you).

Then we'll get a new module, `facts`, which will take create some custom facts we will be using for our configuration. The files are:
- `/etc/puppet/modules/facts/lib/facter/facts.rb`: 
This file will hold ruby code for creating new facters. We'll be using the host fqdn to extract the fields we're interested in. It will extract the environment information from the fqdn and assign it to a "facter". In this example, that will be "env". 
- `/etc/puppet/modules/facts/manifests/init.pp`:
In order to check easily if our facter is working properly, we'll publish a file with all our custom facts. We'll be using a template (the next file)
- `/etc/puppet/modules/facts/templates/factlist.erb`:
This file will be the template for `/etc/facts`, where we'll publish our facters. So far it's only "env".

Then we'll add both classes, "facts" and "ssh" to the common.yaml, as all of our servers will be using them:
- `/etc/puppet/data/common.yaml`: 
Two new lines, adding class "facts" and "ssh"

Then after a while we can see a new /etc/facts file will appear in our servers, showing which env are we in. Once we have this custom fact running, we'll use it for hiera. We'll need to change the hiera.yaml file to add a new origin for config files. The precedence policy is "first one wins" (as if the origins in `hiera.yaml` were applied bottom to top), so we'll put the new origin on top of the `common.yaml` one. And remember: every time you change hiera.yaml, you'll need to restart puppetmaster for it to get the changes. Changes:
- `/etc/puppet/hiera.yaml`: 
There's a new line for the env origin
- `/etc/puppet/data/env/dev.yaml`:
In this file we'll be allowing access to the devs and the devops ssh public keys.
- `/etc/puppet/data/env/prod.yaml`:
In this file we'll be allowing access to the devops ssh public key, and at the same time disallowing dev access to prod.

After a while you'll see how the contents of the `/root/.ssh/authorized_keys` file will match the keys. And if you manually add the devs key to the prod server, it will be erased by puppet.

## Third step: Configuring variables depending on the DataCenter
We usually want to have the most exact time possible in our servers. For that, a low latency to our ntp servers is important. In our example, some of our servers are in one datacenter and some of them are in a different one, so it would be ideal if each server sync'ed the time with the closest ntp server. For that, we'll be setting those variables depending on what datacenter we are.

To continue, in the puppet master, logged as root, type "3" (just a plain number three) and it will checkout the proper git branch with the puppet configuration.

We'll update our "facts" module to get the datacenter we're in. The changes are:
- `/etc/puppet/modules/facts/lib/facter/facts.rb`:
We'll be adding a new snippet for the datacenter info
- `/etc/puppet/modules/facts/templates/factlist.erb`:
We'll be adding the new facter to the file, to confirm it's working as expected.

After that, you can check the `/etc/facts` file in any server to see the new facter addition. Now we'll use that facter for our purpose. The changes:
- `/etc/puppet/hiera.yaml`: 
There's a new line for the datacenter origin (remember to restart puppetmaster after changing hiera.xml file)
- `/etc/puppet/data/datacenter/us-east-1.yaml`:
Here we'll set the ntp config variables for the us-east-1 ntp servers
- `/etc/puppet/data/datacenter/us-wast-1.yaml`:
Here we'll set the ntp config variables for the us-west-1 ntp servers

After a while, you'll see how the `/etc/ntp.conf` file has changed in all servers, and the us-east-1 servers will show different ntp config than us-west-1

## Fourth step: Configuring variables depending on the server role
Now our servers are getting in shape. Next we want to do is to install packages depending on the role they have. Webservers will need apache while database servers will need mysql. As we did before, we can use hiera for that.

To continue, in the puppet master, logged as root, type "4" (just a plain number four) and it will checkout the proper git branch with the puppet configuration.

For this step we'll be using the puppet modules "puppetlabs-apache" and "puppetlabs-mysql" using "puppet module install". The last command (4) have already installed them for you.

Again, we'll update our "facts" module, this time to get the server role. The changes are:
- `/etc/puppet/modules/facts/lib/facter/facts.rb`:
We'll be adding a new snippet for the role info
- `/etc/puppet/modules/facts/templates/factlist.erb`:
We'll be adding the new facter to the file, to confirm it's working as expected.

After that, you can check the `/etc/facts` file in any server to see the new facter addition. Now we'll use that facter for our purpose. The changes:
- `/etc/puppet/hiera.yaml`: 
There's a new line for the role origin (remember to restart puppetmaster after changing hiera.xml file)
- `/etc/puppet/data/role/mysql.yaml`: 
Here we'll set the mysql configurations. For now, we'll just apply the "mysql::server" class so the service gets installed and running
- `/etc/puppet/data/role/apache.yaml`: 
Here we'll set the apache configurations. For now, we'll just apply the "apache" class so the service gets installed and running. 

To access our data over http and confirm it's working, we'll create a webpage showing some info. That will be a simple module called "webpage", with this contents:
- `/etc/puppet/modules/webpage/manifests/init.pp`:
We'll add here the definition of the `/var/www/html/index.html` file with our custom facts. 
- `/etc/puppet/modules/webpage/templates/index.html.erb`:
Text file containing our variables.

At this point we can access our apache servers over http and check the information in them.

## Fifth step: Setting variables just for a particular host
Our cluster of webservers was working ok, but one server started acting up! We want to take it out of the cluster ASAP, and continue with the other hosts, but we'd also like to investigate what's going on with this particular one. No problem! Hiera will help us with that.

To continue, in the puppet master, logged as root, type "5" just a plain number five) and it will checkout the proper git branch with the puppet configuration.

No new puppet modules will be used for this step.

This time we already have a useful facter for our purpose: fqdn. So the changes we'll made are:
- `/etc/puppet/hiera.yaml`: 
There's a new line for the host origin (remember to restart puppetmaster after changing hiera.xml file). This origin will usually be the first line in the hierarchy, as you don't want them to be overwritten by any other file. 


## Sixth step: Mixing environment and role for variables

## Seventh step: Mixing environment and datacenter and roles for variables

## Eighth step: How to control more than one client with the same puppet master




