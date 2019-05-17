# Whats For Dinner? - Catalog Application for Udacity's Full Stack Developer program
* This application  provides the ability for users to create weekly menus to keep track what's for dinner.  Users will have the ability to post, edit and delete their own items.

## Getting Started
* You can *[clone](https://github.com/cmudrenko/WFD_Catalog.git)* or *[download](https://github.com/cmudrenko/WFD_Catalog.git)*.

### Prerequisites
You will need to install these following application in order to make this code work.
* Unix-style terminal
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)

You will also need to download these following files to make it work.
* [VM configuration](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/59822701_fsnd-virtual-machine/fsnd-virtual-machine.zip)

Google API OAuth Credentials need have the user's key information and then files can be updated with resulted JSON file and client secret information.

### Installing

* Unzip the **VM configuration** and you will find a **vagrant** folder
* Use the **Terminal** to get into the **vagrant** folder from **VM configuration**
* run the following command
```sh
$ vagrant up
```
* This will cause Vagrant to download the Linux operating system and install it.
* After it finished and after the shell prompt comes back, you can run this command
```sh
$ vagrant ssh
```
* And this will let you login to the Linux VM. (Please do not shut down the terminal after the login)

### Setting up the enviroment
* Move the folder you downloaded from GitHub and put it into the vagrant folder
* use the following line to get into the vagrant VM folder
```sh
$ cd /vagrant
```
* Use the command line to get in to the folder you just downloaded
* Then you can run the following commands
```sh
$ python database_setup.py
```
```sh
$ python daysnmeals.py
```
* After it added items succesfully, you can run the following command
```sh
$ python project.py
```
* After finish running project.py you can use your favorite browser to visit [WhatsForDinner](http://localhost:8000/)

### Feel free to test out the JSON endpoints
* Returns JSON of all Days of the Week
```sh
(https://localhost:8000/whatsfordinner/JSON)
```
* Returns JSON of a specific day or unassigned and the associated meals
```sh
(https://localhost:8000/whatsfordinner/<int:days_id>/JSON)
```
* Returns JSON of the specific meal details
```sh
(https://localhost:8000/whatsfordinner/<int:days_id>/<int:meal_id>/JSON)
```

