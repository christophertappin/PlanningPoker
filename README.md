# PlanningPoker
A Scrum Planning Poker app
## Prerequisites ##
* Install Python 3 - I used 3.7.5 and have tested only with this version - https://www.python.org/downloads/release/python-375/
* Install and start redis. I used docker
```
docker run -p 6379:6379 -d redis:2.8
```
## Installation ##
* Download the zip archive and extract, or clone the repository
* `cd` into the `PlanningPoker` directory
* Create a virutal environment
```
python3 -m venv env
```
* Activate virtual environment
```
source env/bin/activate
```
* Install python requirements
```
pip install -r requirements.txt
```
* `cd` into `planning_poker`
* Setup the database
```
python manage.py makemigrations
python manage.py migrate
```
* Start the server
```
python manage.py runserver
```
* Follow the url provided
