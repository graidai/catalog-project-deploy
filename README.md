Cat-A-Log App - A Udacity project to keep the record of sports items. Created using Python Flask framework.
The website lets the user navigate through different items in the sports categories available on the left side of the jumbo display. The right column displays the items for the selected category. Anyone can view the items in the catalog. However, one has be logged in to be able to create, edit or delete the items in the catalog. Also, one is only allowed to edit or delete an item if it was created by the respective user.

As of the moment, users are only allowed to do CRUD operations on the items. Users cannot create a new categories yet. Authentication is provided by Google OAuth.

Files in the project in Catalog Folder:
1 - app.py - the primary app file
2 - database_setup.py - setup database structure
3 - item_builder.py - python program to build the starter database
4 - html files - in template folder
5 - styles and image files - in static folder

File application.py builds the main server. The file contains all the routes to the html pages, google-oauth, and API endpoints.

File item_builder.py will give the user the starter database. However, it is not required if you also copied itemsDatabase.pyc from this git repo. It already has quite a bit of sports catalog.

Due to the problem of static files not updating browser cache, following flask snippet had to implemented to have a smooth style editing (instead of destroying vagrant and setting up vagrant all over again).
http://flask.pocoo.org/snippets/40/
https://stackoverflow.com/questions/32132648/python-flask-and-jinja2-passing-parameters-to-url-for
Once the website is deployed in its final stage, the implemented snippet is not really required.

## Instructions to setup google OAuth
Create a new project in Google Developer Console.
Goto google API services, on credentials click on Create credentials -> OAuth client ID. On Authorized Javascript Origins, put in your local host. eg, http://localhost:8000
From the created Client ID, copy Client ID and replace data-clientid="*********.apps.googleusercontent.com" in templates/login.html.
Also, click on Download JSON, to download the client's secret. Change the name of the downloaded file to client_secrets and replace the current file of the same name in catalog folder.
Finish OAuth consent screen in google console credentials by just typing the name of the project in the [Product name show to user] form.


## Instructions to run the program.

The program is setup to run in VM environment of VirtualBox managed by Vagrant.

If you don't have the virtualmachine already in system, install [VirtualBox](https://www.virtualbox.org/wiki/Downloads). Install Platform Package for you operating system. Extension pack is not required.

Install [Vagrant](https://www.vagrantup.com/downloads.html) for your operating system. If possible install older version 1.9.1 which is more stable.


## Download the project with the VM configuration
Fork and clone the current project/or download the file.

enter command [vagrant up] which will take a few minute to download the Linux OS in the VM. Once the VM is up and running, run [vagrant ssh] to log in the Linux VM.

Once in the vm terminal, run command [cd /vagrant] "the '/' from vagrant is important" to access the shared local directory.
cd to Database_project
run python application.py

## Access the API endpoint of this project
http://localhost:8000/catalog.JSON
