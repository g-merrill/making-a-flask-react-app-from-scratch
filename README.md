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
2) Create your repo on Github

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
* __Note:__ Anytime that you close and reopen the terminal/project, you can get the app running locally again with the following terminal commands:
```
$ pipenv shell
$ export FLASK_APP=api
$ export FLASK_DEBUG=1
$ flask run
```
10) Use [Postman](https://youtu.be/MdyJn4EKfc4) to verifty that the POST route is working by making a POST request of anything you want (like {"test": "test"}) to localhost/5000/api/add_post. If it returns "Done" then it is working! 

## Setting Up Heroku

11)  Open [Heroku](https://dashboard.heroku.com/) dashboard

12)  new>Create new app

13)  Give it a name and hit Create app

14)  Under Deployment method, select GitHub

15)  Connect to GitHub by search for your repo

16)  Once you have found the repo you are using, click Connect

17)  Under Automatic deploys, click Enable Automatic Deploys

18)  Back in VS Code terminal :
```
$ pipenv install gunicorn
$ touch wsgi.py
```
19) Inside wsgi.py :
```
from api import create_app

app = create_app()
```
20)
```
$ touch Procfile
```
21) Inside Procfile :
```
web: gunicorn wsgi:app
```
22) Commit and push changes
* If not already automatically starting build and deploying:

22a) Under manual deploy, click Deploy Branch

23) Once deployed, go to the deployed url by clicking Open app at the top of the page
* Should see Not Found because you haven't set up the root route at '/'

24) If you navigate to '/api/items' you should see:
```
{
	items: [ ]
}
```
just like it showed locally!

## Setting Up Postgres via Heroku

25) On the Heroku app page, click Overview tab

26) In Installed add-ons section, click Configure Add-ons

27) In the Add-ons search bar, type 'postgres'

28) 'Heroku Postgres' should be available, click that

29) Select the plan you would like (Hobby Dev is free)

30) Click Provision

31) In Settings tab, under Config Vars, click reveal Config Vars

32) Click the edit button

33) Copy the value of the DATABASE_URL

34) Exit edit screen

35) In VS Code:
```
$ pipenv install python-dotenv
$ touch .env
```
36) in .env :
```
DATABASE_URL=<copied db url value>
```

## Setting Up SQLite Database Locally

37) in api/\_\_init\_\_.py, refactor the code to look like the following :
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
38)
```
$ pipenv install psycopg2
```
38b) If that fails :
```
$ pipenv uninstall psycopg2
$ pipenv install psycopg2-binary
```
39)
```
$ touch api/models.py
```
40) inside api/models.py :
```
from . import db

class Item(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  description = db.Column(db.String(250))
```

## Item Create Route (The 'C' in CRUD)

1)  In api/views.py, make the following changes :
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
48)
```
$ flask run
```

* Okay now we are going to get things up and running on your app deployed on heroku with the Postgres db

58)
```
$ touch api/commands.py
```
1)  inside api/commands.py :
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
60) Refactor api/\_\_init\_\_.py with the commands lines :
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

In the terminal, type 'flask reset_items'

49) Open Postman
50) Change method to POST and navigate to http://localhost:5000/api/add_item
51) Click the Body tab
52) Make sure the dropdown on the right is set to JSON
53) Select 'raw' as the input type and enter something like :
```
{ 
	"name" : "Greg",
	"description" : "Learning how to build a flask/react app from scratch!"
}
```
54) Click send
* Should receive the Done message if everything works out

## Item Read-All Route (The 'R' in CRUD)

1)  In api/views.py :
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
* Remember to have server running via the 'flask run' command
* Now in Postman, the '/api/items' get request should show the data you entered!

61) Git commit, push, and wait for Heroku to rebuild/redeploy

62) Navigate to your deployed url + '/api/items'
* And you should see:
```
{
	items: [ ]
}
```
* Back in Heroku, you may need to add a SECRET_KEY as another config var, you can make it any random string that you would like (I am unsure if this is actually needed or not, since my other flask/react apps haven't needed one)
* __Note:__ If you want to reset on the local server side, type 'flask reset_items' and then 'flask run'

## Set Up React Frontend
* You should be all set up to build out the React frontend now!
* in the VS terminal, keep the flask backend running on one terminal
66) Open up a new terminal and type:
```
$ npx create-react-app react-frontend
$ cd react-frontend
$ npm start
```
67) Open up another new terminal and type : 
```
$ cd react-frontend/
$ npm i semantic-ui-react semantic-ui-css
```
68) In index.js, add this import to the rest of the imports:
```
import 'semantic-ui-css/semantic.min.css';
```
69) In package.json, add the proxy as so:
```
…
  },
  "proxy": "http://localhost:5000",
  "browserslist": {
…
```
* In the terminal, make sure you are still in /react-frontend
70) Do the following commands :
```
$ mkdir src/components
$ touch src/components/ItemForm.js
$ touch src/components/Items.js
```
71) In ItemForm.js :
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
72) In Items.js :
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
73) Refactor App.js as so: 
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
74) Delete the logo.svg file and README.md files
75) In App.css :
```
.App {
  text-align: center;
}
```
76) Git commit and git push - almost there!

## Npm Eject

* Now that we have a front end that we are happy with and don't anticipate needing the React hot-reloading much more, it's time to build this out to be served by our Flask backend.  Again, you will lose the handy React hot-reloading on localhost:3000 with npm start by using this method, so be sure to have your frontend in a relatively finished state before doing these final steps.  After these steps, you can still make changes to the frontend, but they must be applied manually with a terminal command and a small wait time.
1)  In the terminal, at the root level :
```
$ mkdir api/static
$ mkdir api/templates
```
78) In api/views.py, add a home route as such:
```
from flask import Blueprint, jsonify, request, render_template

…

@api.route('/')
def my_index():
  return render_template('index.html', token='Hello Flask+React')

…
```
79) git commit and push before doing the following
80) In the terminal :
```
$ cd react-frontend/
$ npm run eject
```
81) When prompted to confirm, type y
82) Once completed, in config/paths.js around line 72, change appBuild to:
```
  appBuild: resolveApp('../api/static/react'),
```
83) In web pack.config.js, control+F and command+D for 'static/' as necessary and erase them all, there should be around 8 of them
84) Down around line ~528, in plugins: [ new HtmlWebpackPlugin( Object.assign etc, beneath the inject and template lines, write the following:
```
          filename: '../../templates/index.html',
```
85) In public/index.html, underneath the <title> tag, write :
```
    <script>window.token = "{{ token }}"</script>
```
86) In the react frontend, in App.js, can put the following anywhere you want to test if things are properly working :
```
      <p>My Token = { window.token }</p>
```
87) In package.json, add a homepage top-level variable:
```
… 
  "private": true,
  "homepage": "/static/react",
  "dependencies": {
…
```
88) Making sure you are in the react frontend directory, in the terminal, type :
```
npm run build
```
89) Install any necessary packages that you are prompted to
* You should see a react folder in the api/static folder now and and index.html in the templates folder
* __Note:__ Anytime you make any changes to your react frontend, you need to do 'npm run build' to update the actually served files inside the api directory
90) Start up your flask backend
91) Browse to localhost:5000
* You should see your react frontend with the sample token message!
92) git commit and push and wait for Heroku to rebuild/redeploy

## Done!
**Congrats, you made it to the end of this guide!**
**Check out your shiny new deployed Flask/React app!!!**

[Deployed Link!](https://flask-react-app-from-scratch.herokuapp.com/)

This app creation process was written out after completing the following code-alongs with Anthony Herbert (Pretty Printed), Ben Awad, and Joran Beasly: [Flask Movie API Example](https://youtu.be/Urx8Kj00zsI) | [How to Call a Flask API in React](https://youtu.be/06pWsB_hoD4) | [Deploy a Flask App to Heroku With a Postgres Database](https://youtu.be/FKy21FnjKS0) | [Serving React with a Flask Backend](https://youtu.be/YW8VG_U-m48)