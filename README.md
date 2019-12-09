## Setting Up Flask App and GitHub

1) 
```
$ mkdir flask-react-app
$ cd flask-react-app
$ git init && code .

$ pipenv install flask flask-sqlalchemy
$ pipenv shell

$ git add . && git status
$ git commit -m 'Initial commit'
```
2) Create your repo on [Github](https://github.com/new)

3)
```
$ git remote add origin https://github.com/<yourgithubusername>/<yourreponame>.git
$ git push -u origin master

$ mkdir api
$ export FLASK_APP=api
$ export FLASK_DEBUG=1
$ touch api/__init__.py
```
4) inside api/\_\_init\_\_.py :
```
from flask import Flask

def create_app():
  app = Flask(__name__)

  return app
```
## Setting Up Initial Routes

5)
```
$ touch api/views.py
```
6) Inside api/views.py :
```
from flask import Blueprint, jsonify

api = Blueprint('api', __name__)

@api.route('/api/add_item', methods=['POST'])
def add_item():

  return 'Done', 201

@api.route('/api/items')
def items():

  items = []

  return jsonify({ 'items': items })
```
7) inside api/\_\_init\_\_.py, modify the create_app function :
```
def create_app():
  app = Flask(__name__)

  from .views import api
  app.register_blueprint(api)

  return app
```
8) In the terminal :
```
$ flask run
```
9) Navigate to http://localhost:5000/api/items

* You should see :
```
{
  items: []
}
```
* __Note:__ Anytime that you close and reopen the terminal/project, you can get the app running locally again with the following terminal commands:
```
$ pipenv shell
$ export FLASK_APP=api
$ export FLASK_DEBUG=1
$ flask run
```
* Use [Postman](https://youtu.be/MdyJn4EKfc4) to verify that the POST route is working

10)  Open Postman

11)  Change method to POST and navigate to http://localhost:5000/api/add_item

12)  Click the Body tab

13)  Make sure the dropdown on the right is set to JSON

15)  Select 'raw' as the input type and enter something like :
```
{
  "test": "Expecting Done, 201 response"
}
```
16) Click Send
* If it returns "Done" then it is working! 

## Setting Up Heroku

17)  Open [Heroku](https://dashboard.heroku.com/) dashboard

18)  new>Create new app

19)  Give it a name and hit Create app

20)  Under Deployment method, select GitHub

21)  Connect to GitHub by searching for your repo

22)  Once you have found the repo you are using, click Connect

23)  Under Automatic deploys, click Enable Automatic Deploys

24)  Back in VS Code terminal :
```
$ pipenv install gunicorn
$ touch wsgi.py
```
25) Inside wsgi.py :
```
from api import create_app

app = create_app()
```
26)
```
$ touch Procfile
```
27) Inside Procfile :
```
web: gunicorn wsgi:app
```
28) Commit and push changes
* If not already automatically starting build and deploying:

28a) Under manual deploy, click Deploy Branch

29) Once deployed, go to the deployed url by clicking Open app at the top of the page
* Should see Not Found because you haven't set up the root route at '/'

30) If you navigate to '/api/items' you should see:
```
{
	items: [ ]
}
```
just like it showed locally!

## Setting Up Postgres via Heroku

31) On the Heroku app page, click Overview tab

32) In Installed add-ons section, click Configure Add-ons

33) In the Add-ons search bar, type 'postgres'

34) 'Heroku Postgres' should be available, click that

35) Select the plan you would like (Hobby Dev is free)

36) Click Provision

37) In Settings tab, under Config Vars, click reveal Config Vars

38) Click the edit button

39) Copy the value of the DATABASE_URL, it should begin with 'postgres://'...

40) Exit edit screen

41) In VS Code:
```
$ pipenv install python-dotenv
$ touch .env
```
42) in .env file :
```
DATABASE_URL=<copied db url value>
```

## Setting Up the Database Locally

43)
```
$ pipenv install psycopg2
```
43b) If that fails to install, do the following :
```
$ pipenv uninstall psycopg2
$ pipenv install psycopg2-binary
```
44) in api/\_\_init\_\_.py, refactor the code to look like the following :
```
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
  app = Flask(__name__)
  
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

  db.init_app(app)

  from .views import api
  app.register_blueprint(api)

  return app
```
45)
```
$ touch api/models.py
```
46)  inside api/models.py :
```
from . import db

class Item(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  description = db.Column(db.String(250))
```
47)
```
$ touch api/commands.py
```
48)  inside api/commands.py :
```
import click
from flask.cli import with_appcontext

from . import db
from .models import Item

@click.command(name='reset_items')
@with_appcontext
def reset_items():
  db.drop_all()
  db.create_all()
```
49) Refactor api/\_\_init\_\_.py with the commands lines :
```
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .commands import reset_items

def create_app():
  app = Flask(__name__)

  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
  
  db.init_app(app)

  from .views import api
  app.register_blueprint(api)

  app.cli.add_command(reset_items)

  return app
```
50) In the terminal, type 
```
$ flask reset_items
```
* running this command should create the items table in your postgres db for the first time

## Item Create Route (The 'C' in CRUD)

51)  In api/views.py, make the following changes :
```
from flask import Blueprint, jsonify, request
from . import db
from .models import Item

…

@api.route('/api/add_item', methods=['POST'])
def add_item():
  item_data = request.get_json()

  new_item = Item(name=item_data['name'], description=item_data['description'])

  db.session.add(new_item)
  db.session.commit()

  return 'Done', 201

…
```
52)
```
$ flask run
```
53) Open Postman

54) Change method to POST and navigate to http://localhost:5000/api/add_item

55) Click the Body tab

56) Make sure the dropdown on the right is set to JSON

57) Select 'raw' as the input type and enter something like :
```
{ 
	"name" : "Yourname",
	"description" : "Learning how to build a flask/react app from scratch!"
}
```
58) Click send
* Should receive the Done message if everything works out

## Item Read-All Route (The 'R' in CRUD)

59)  In api/views.py :
```
…

@api.route('/api/items')
def items():
  items_list = Item.query.all()
  items = []

  for item in items_list:
    items.append({ 'name': item.name, 'description': item.description })

  return jsonify({ 'items': items })

…
```
* Remember to have your server running via the 'flask run' command

60) In Postman, change the request method to GET

61) Type '/api/items' in the address bar 
* should show the JSON data you entered!

62) Git commit, push, and wait for Heroku to rebuild/redeploy

63) Navigate to your deployed url + '/api/items'
* You should also see the JSON data you entered in Postman!
* __Note:__ If you want to reset your database via the command line, type :
```
$ flask reset_items
$ flask run
```
## Set Up React Frontend
* You should be all set up to build out the React frontend now!
* in the VS terminal, keep the flask backend running on one terminal

64)  Open up a new terminal and type:
```
$ npx create-react-app react-frontend
$ cd react-frontend
$ npm start
```
65) Open up another new terminal and type : 
```
$ cd react-frontend/
$ npm i semantic-ui-react semantic-ui-css
```
66) In index.js, add this import to the rest of the imports:
```
import 'semantic-ui-css/semantic.min.css';
```
67) In package.json, add the proxy as so:
```
…
  },
  "proxy": "http://localhost:5000",
  "browserslist": {
…
```
* In the terminal, make sure you are still in /react-frontend
68) Do the following commands :
```
$ mkdir src/components
$ touch src/components/ItemForm.js
$ touch src/components/Items.js
```
69) In ItemForm.js :
```
import React, { useState } from 'react';
import { Form, Input, Button } from 'semantic-ui-react';

export const ItemForm = ({ onNewItem }) => {
  const [ name, setName ] = useState('');
  const [ description, setDescription ] = useState('');
  return (
    <Form>
      <Form.Field>
        <Input 
          placeholder="item name"
          value={name}
          onChange={e => setName(e.target.value)}
        />
      </Form.Field>
      <Form.Field>
        <Input 
          placeholder="item description"
          value={description}
          onChange={e => setDescription(e.target.value)}
        />
      </Form.Field>
      <Form.Field>
        <Button 
          onClick={async () => {
            const item = {name, description};
            const response = await fetch('/api/add_item', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(item)
            });
            if (response.ok) {
              console.log('response worked!');
              onNewItem(item);
              setName('');
              setDescription('');
            }
          }}
        >submit</Button>
      </Form.Field>
    </Form>
  );
}
```
70) In Items.js :
```
import React from 'react';
import { List, Header } from 'semantic-ui-react';

export const Items = ({ items }) => {
  return (
    <List>
      {items.map(item => {
        return (
          <List.Item key={item.name}>
            <Header>{item.name}</Header>
            <p>{item.description}</p>
          </List.Item>
        );
      })}
    </List>
  );
}
```
71) Refactor App.js as so: 
```
import React, { useEffect, useState } from 'react';
import './App.css';
import { Items } from './components/Items';
import { ItemForm } from './components/ItemForm';
import { Container } from 'semantic-ui-react';

function App() {
  const [items, setItems] = useState([]);
  useEffect(() => {
    fetch('/api/items').then(res => 
      res.json().then(data => {
        setItems(data.items)
      })
    );
  }, []);
  return (
    <Container 
      style={{ marginTop: 40 }}
      className='App'
    >
      <ItemForm 
        onNewItem={item => setItems(currentItems => [item, ...currentItems])} />
      <Items 
        items={ items }
      />
    </Container>
  );
}

export default App;
```
72) Delete the logo.svg file and README.md files

73) In App.css :
```
.App {
  text-align: left;
}
```
74) Git commit and git push - almost there!

## Npm Eject

* Once you are happy with your React frontend, it's time to use npm run build to serve our frontend work with our Flask backend.  However, to get the index.html to be written to the backend directory, 'api', we will need to do npm run eject.  By doing so, you will lose the handy React hot-reloading on localhost:3000 with npm start by using this method, but we will do a workaround to be able to keep it!  So at this point, we will split the project into two branches, a frontend branch and the master branch.  The master branch will be the branch we do npm run eject from, and we'll merge any additional React frontend changes in from the unejected React-friendly frontend branch if need be.

75) Create a new branch in the terminal :
```
$ git branch frontend
```
76)  We should still be on the master branch. Again in the terminal, at the root level :
```
$ mkdir api/static
$ mkdir api/templates
```
77) In api/views.py, add a home route as such:
```
from flask import Blueprint, jsonify, request, render_template

…

@api.route('/')
def home():
  return render_template('index.html', token='Hello Flask+React')

…
```
78) git commit and push ejected branch to origin before doing the following

79) In the terminal :
```
$ cd react-frontend/
$ npm run eject
```
80) When prompted to confirm, type y

81) Once completed, in config/paths.js around line 72, change appBuild to:
```
  appBuild: resolveApp('../api/static/react'),
```
82) In web pack.config.js, control+F and command+D for 'static/' as necessary and erase them all, there should be around 8 of them

83) Down around line ~520-528, in plugins: [ new HtmlWebpackPlugin( Object.assign etc, beneath the inject and template lines, write the following:
```
          filename: '../../templates/index.html',
```
84) In public/index.html, underneath the <title> tag, write :
```
    <script>window.token = "{{ token }}"</script>
```
85) In the react frontend, in App.js, can put the following anywhere you want to test if things are properly working :
```
      <p>My Token = { window.token }</p>
```
86) In package.json, add a homepage top-level variable:
```
… 
  "private": true,
  "homepage": "/static/react",
  "dependencies": {
…
```
87) Making sure you are in the react frontend directory, in the terminal, type :
```
npm run build
```
* Install any necessary packages if you are prompted to
* You should now see a react folder in the api/static folder now and and index.html in the templates folder

88)  Start up your flask backend

89) Browse to http://localhost:5000
* You should see your react frontend with the sample token message!

90)  git commit and push and wait for Heroku to rebuild/redeploy

**Check out your shiny new deployed Flask/React app!!!**

## Making Further Frontend Changes in React

91) Switch to frontend branch
```
$ git checkout frontend
```
* This branch should be non-ejected, so you should have access to the instant reload while making frontend changes on localhost:3000 using npm start
* potential [bugfix](https://stackoverflow.com/a/42539669/12498743) with node_modules needing to be deleted and reinstalled:

92) Make any desired frontend changes

93) In the terminal :
```
$ git add . && git status
$ git commit -m 'Some description of changes'
$ git checkout master
$ git merge frontend
:wq
$ cd react-frontend && npm run build && cd .. && pipenv shell
$ export FLASK_APP=api && export FLASK_DEBUG=1 && open http://localhost:5000 && flask run
```
94)  Git commit, push, and wait for Heroku to rebuild/redeploy

## Done!

**Congrats, you made it to the end of this guide!**

[Deployed Link!](https://flask-react-app-from-scratch.herokuapp.com/)

This app creation process was written out after completing the following code-alongs with Anthony Herbert (Pretty Printed), Ben Awad, and Joran Beasly: [Flask Movie API Example](https://youtu.be/Urx8Kj00zsI) | [How to Call a Flask API in React](https://youtu.be/06pWsB_hoD4) | [Deploy a Flask App to Heroku With a Postgres Database](https://youtu.be/FKy21FnjKS0) | [Serving React with a Flask Backend](https://youtu.be/YW8VG_U-m48)