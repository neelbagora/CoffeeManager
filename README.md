# CoffeeManager
CoffeeManager for CS348

## For local development:

0. Have mySQL and Django installed on your local machine
1. Clone this repository
2. Create a coffeemanager database in your local mysql
3. Change the password in the DATABASES in coffee/settings.py to your mySQL root password
 ![image](https://user-images.githubusercontent.com/54249775/158683484-e30f3243-966c-46c2-b115-be71b7201c00.png)
4. Run `python manage.py migrate`
5. To run the project `python manage.py runserver`

## Project Structure
1. coffee directory is the djangoproject directory
2. coffeemanager is the djangoapp directory, all the main code is inside this
3. coffeemanager/templates iinclude all the html files
4. coffeemanager/models.py include the schema, more schemas to be added as we progress
5. coffeemanager/views.py contain all the code for rendering each view
6. coffeemanager/urls.py has the index of all urls currently served by the project


