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

Files changed:
- /etc/puppet/hiera.yaml: In this file we're describing where hiera should look for config files with classes and variables to apply to the servers in our infrastructure, and the precedence of them. More details in [the hiera.xml section in puppet docs](https://docs.puppetlabs.com/hiera/3.0/configuring.html)
- /etc/puppet/data/common.yaml: This path is included in hiera. Classes and variables on this file will be applied to all servers.

## Second step: Configuring variables depending on the environment
In this step 

## Third step: Configuring variables depending on the DataCenter

## Fourth step: Configuring variables depending on the server role

## Fifth step: Setting variables just for a particular host

## Sixth step: Mixing environment and role for variables

## Seventh step: Mixing environment and datacenter and roles for variables

## Eighth step: How to control more than one client with the same puppet master




