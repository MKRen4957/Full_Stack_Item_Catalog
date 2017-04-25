The application is a web application that provides a list of items within a
variety of categories.
- It built in Python 2.7, implemented libraries Flask 0.10.0 and SQLAlchemy
- The project contains a static folder for css files, a templates folder for
template html files, application.py to run the program, database.py to create
the database, addcategories.py to populate initial data into the database

The project requires to setup Google OAuth service, instruction as following:
1. Go to https://cloud.google.com (google login is required)
2. Click "Console" on the top right corner
3. On the top ribbon, next to Google Cloud Platform, click on the dropdown menu,
click on the + sign on the top right corner to create a new project.
4. Once the project is created, choose API Manager in the left hamburger icon
5. Click on "Credentials"
6. Click on Create Credentials -> OAuth client ID -> Web application
7. Under Authorized JavaScript origins, type in http://localhost:5000,
Under Authorised redirect URIs, type in http://localhost:5000/auth/oauth2callback
8. After save the changes, Download file as JSON, button is on the right
9. Rename the downloaded file to "client_secrets.json" and replace
the original client_secrets.json file.
10. In login.html file, on line 16, change the data-clientid to your clientID
shown in your Google Cloud Platform where you downloaded the JSON file.

Please follow the instruction below to run the application.
1. Clone/download the depository.
2. Change directory to where the files are downloaded.
3. Change directory into vagrant folder by typing “cd vagrant”
4. Type in “vagrant up”
5. Type in “vagrant ssh”
6. Change the directory by typing in “cd /vagrant/catalog”
7. Note: you may need to delete the itemcatalog.db file to have a fresh application
8. Run the database by typing in “python database.py”
9. Add initial entries into the database by typing in “addcategories.py”
10. Run the program by typing in “python application.py”
11. To see the website and see the catalog, open your browser and type in “localist:5000” in the url
