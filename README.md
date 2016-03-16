# "How does puppet work with hiera?" lab
This lab is aimed for those people who don't know hiera. This is a practical example with real life (tm) examples. It will get you running on the basics of hiera/puppet, and you can get going from there.

## What is hiera? What can I use hiera for? what is an ENC (external node classifier)?
[Hiera](https://github.com/puppetlabs/hiera) is basically a hierarchical key/value store, but used in conjunction with Puppet, it can serve the purpose of ENC or "External node classifier".
According to [puppet documentation](https://docs.puppetlabs.com/guides/external_nodes.html): "An external node classifier is an arbitrary script or application which can tell Puppet which classes a node should have.It can replace or work in concert with the node definitions in the main site manifest (site.pp).". So basically you can use hiera to store which classes should be applied to which servers.

## What's the objective of this lab?
We'll set up an environment where we will be able to experiment with different ways of structuring the configuration of our servers. We'll extract information about them (mostly from their servername) as a fact, and then we'll use that information to configure them depending on their datacenter, the environment they're in, the role of the server, and so on. 

## Lab layout
In this lab we'll try to work with a real web environment we can see every day. That means:

- We'll have different server roles: webservers and mysql servers. 
- We'll fake two different datacenters: us-east-1 and us-west-1 (just faking it, because all servers are actually in the same aws region, in Europe). 
- We'll consider 3 different environments: dev, stage and prod.
- We'll consider 2 different domain names, so we can consider we're covering 2 different clients (or 2 different websites from the same client). The names are: client1 and client2.

The servername syntax for client1 will be RoleNumber.datacenter.environment.domain. Example: webserver2.us-east-1.prod.client1.com
The servername syntax for client2 will be intentionally different to show some more possibilities, being EnvRoleNumber.domain. Example: pweb1.client2.com

All of them will be connected to the same puppet master. We won't discuss here if this layout is secure or if it can be improved, as it's just a test environment to learn about puppet and hiera.

This environment will be created by a python script: create_hiera_env.py. It will create 7 aws instances, type 't2.micro' so we can use the aws free tier. 
There is also a "delete_hiera_env.py" script so we can just delete all servers in our lab and not incur into expenses. Don't forget to run it when you're done with the lab!

## Requirements for this lab
This lab will be using python to create some servers in Amazon AWS. Those servers will be micro size, so they'll be on the free-tier (they won't cost you money if your aws account is younger than a year).

You need to have installed in your computer:
- python >= 2.7 
- boto python library = 2.x

Then you'll need the "[create_hiera_env.py](https://github.com/ersiko/puppet-hiera-lab/blob/master/create_hiera_env.py)" script

Also, regarding AWS, you'll need:
- an AWS account, and an "access_key" / "secret_access_key" pair with ec2 and vpc privileges, set inside the exportenv.sh file.
- a ssh public / private key pair. You'll need to set the key name and key path inside the exportenv.sh file.
- it's best to set this file with 600 permissions (chmod 600 exportenv.sh), and we've added this to the .gitignore also.


# Preparation
After meeting the requirements and editing the exportenv.sh script, simply run the command:

    source exportenv.sh

Then you can run the [create_hiera_env.py](https://github.com/ersiko/puppet-hiera-lab/blob/master/create_hiera_env.py) script, and it'll create the needed aws instances.

After all the instances are running, the script will output the lines you'll need to connect to all the servers. Just copy and paste the lines.

When you're done with your lab, don't forget to remove all the servers. There's another script for that: [delete_hiera_env.py](https://github.com/ersiko/puppet-hiera-lab/blob/master/delete_hiera_env.py)

## Confirming the env is working
Once the script finished, it will still take 4-5 minutes for all the servers to be properly configured. To confirm they are, connect to the puppetmaster and run:
    
    sudo puppet cert --list --all

That will show you the list of running instances. It should have 8 entries. If it does, then you're goot to go, and can start with the lab!

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
There's a new line for the host origin (remember to restart puppetmaster after changing hiera.xml file). This "hosts" origin will usually be the first line in the hierarchy, as you don't want them to be overriden. 
- `/etc/puppet/data/hosts/webserver1.us-east-1.prod.client1.com.yaml`:
In this file we'll set the variables to this particular server. Just two lines to make sure apache is stopped and it won't start if the server reboots.

Now you can check how webserver1.us-east-1.prod.client1.com has apache stopped while webserver2.us-east-1.prod.client1.com is up and running (and all the other servers, too). We also could uninstall apache and install and configure nginx if we wanted to test how apache performs against nginx on the same load.

## Sixth step: Mixing environment and role for variables
Ok, now we have our apache servers running, and we want them to connect to mysql. Our app has a config file where we put the connection string. But the dev webservers must connect to the dev mysql servers, and the prod webservers to the prod mysql. And we can't use only the "env" facter, because each environment has other roles than webservers. How can we fix that? Easy, just mixing "env" and "roles" facters.

To continue, in the puppet master, logged as root, type "6" just a plain number six) and it will checkout the proper git branch with the puppet configuration.

No new puppet modules will be used for this step.

Again, no new facters. The changes are in:
- `/etc/puppet/hiera.yaml`: 
There's a new line for the env/role origin (remember to restart puppetmaster after changing hiera.xml file).
- `/etc/puppet/modules/webpage/manifests/init.pp`:
We're adding a new parameter for our class "webpage" for the connection string.
- `/etc/puppet/data/modules/webpage/templates/index.html.erb`:
We're adding the connection string to the webpage so we can confirm it's working.
- `/etc/puppet/data/env/prod/role/webserver.yaml`:
Just adding the webpage::connection_string variable, setting it to connect to a prod server.
- `/etc/puppet/data/env/dev/role/webserver.yaml`:
Just adding the webpage::connection_string variable, setting it to connect to a dev server.

Now you can check all prod an dev servers how they get their own mysql server to connect to.

## Seventh step: Mixing environment and datacenter and roles for variables
Our mysql server was a bit overloaded and it wasn't performing well on the cross-datacenter read queries, so we decided to spin up a read-replica in the same datacenter as the webservers. All write queries will still go to the mysql master, but the reads will be dramatically improved. How can we do that? Exactly the same way we've been doing it so far.

To continue, in the puppet master, logged as root, type "7" just a plain number seven) and it will checkout the proper git branch with the puppet configuration.

No new puppet modules will be used for this step.

Again, no new facters. The changes are in:
- `/etc/puppet/hiera.yaml`: 
There's a new line for the datacenter/env/role origin (remember to restart puppetmaster after changing hiera.xml file). This is only an example, for real life (tm) you will probably set it in a different order, or a different directory, in a way that fits better your needs.
- `/etc/puppet/data/datacenter/us-west-1/env/prod/role/webserver.yaml`:
Here we're setting the new connection string for the us-west-1 datacenter prod webservers

And we can check now in the webpage how are they both connecting to different servers.

## Eighth step: How to control more than one client with the same puppet master
Perfect! We have our modules and our configurations... great! Now I'd like to use all my effort in all the websites I'm managing. But they're all different clients, different domains and different name format... Could we add those servers to our puppet master? Yeah, of course!

To continue, in the puppet master, logged as root, type "8" just a plain number six) and it will checkout the proper git branch with the puppet configuration.

For this step we'll be using the puppet module "nodes-php". The last command (8) have already installed them for you.

We'll add one new facter called "client", but not only that. As the name format is different (webserver1.prod.us-east1.client1.com vs pweb1.client2.com), we'll need to add some extra code to our existing facters to adapt to both formats, changing the following files:

- `/etc/puppet/modules/facts/lib/facter/facts.rb`: 
Here we're adding the "client" facter. Then we add some conditional statements so we extract the values from the fqdn in different ways for both clients.
- `/etc/puppet/modules/facts/templates/factlist.erb`:
Adding the new "client" facter to the "/etc/facts" file so we can confirm it's working.
- `/etc/puppet/hiera.yaml`: 
There's a new line for the client/role origin (remember to restart puppetmaster after changing hiera.xml file). 
- `/etc/puppet/data/role/webserver.yaml`:
We're installing here php and adding the php::extension::mysql class that will be used in all webservers, no matter what client they are.
- `/etc/puppet/data/client/client1/role/webserver.yaml`:
This client uses memcached, so we're adding the memcached php module to their webservers.
- `/etc/puppet/data/client/client2/role/webserver.yaml`:
This client uses redis instead of memcached, so we're adding the redis php module to their webservers.

Et voilà! We're managing two clients re-using our modules and our main configuration but also being able to adapt to their particularities. All set!
