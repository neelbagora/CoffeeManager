# CoffeeManager
CoffeeManager for CS348

## For local development:

0. Have mySQL and Django installed on your local machine
1. Clone this repository
2. Download the Cloud SQL Auth Proxy: https://cloud.google.com/sql/docs/mysql/connect-admin-proxy
3. KEY_FILE is the file I sent on groupme
4. Run this command:
`./cloud_sql_proxy -credential_file="[PATH_TO_KEY_FILE]" -instances=cs348-coffeemanager:us-central1:coffeetables=tcp:1234`
5. Run `python manage.py migrate`
6. If the above command gives you errors make sure you have installed all the required python packages 
7. To run the project `python manage.py runserver`


## Project Structure
1. coffee directory is the djangoproject directory
2. coffeemanager is the djangoapp directory, all the main code is inside this
3. coffeemanager/templates include all the html files
4. coffeemanager/models.py include the schema, more schemas to be added as we progress
5. coffeemanager/views.py contain all the code for rendering each view
6. coffeemanager/urls.py has the index of all urls currently served by the project


