```
$ mkdir flask-react-app
$ cd flask-react-app
$ git init && code .

$ pipenv install flask flask-sqlalchemy
$ pipenv shell

$ git add . && git status
$ git commit -m 'Initial commit'
```
* Create your repo on Github
```
$ git remote add origin https://github.com/<yourgithubusername>/<yourreponame>.git
$ git push -u origin master

$ mkdir api
$ export FLASK_APP=api
$ export FLASK_DEBUG=1
$ touch api/__init__.py
```
* inside api/\_\_init\_\_.py :
```
from flask import Flask

def create_app():
  app = Flask(__name__)

  return app
```


```
$ touch api/views.py
```
* Inside api/views.py :
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
* inside api/\_\_init\_\_.py, modify the create_app function :
```
def create_app():
  app = Flask(__name__)

  from .views import api
  app.register_blueprint(api)

  return app
```
* In the terminal :
```
$ flask run
```

* Navigate to http://localhost:5000/api/items
* **Note:** Anytime that you close and reopen the terminal/project, you can get the app running locally again with the following terminal commands:
```
$ export FLASK_APP=api
$ export FLASK_DEBUG=1
$ flask run
```
* You can verify the POST route is working via Postman


* Open heroku dashboard
* new>Create new app
* Give it a name and hit Create app
* Under Deployment method, select GitHub
* Connect to GitHub by search for your repo
* Once you have found the repo you are using, click Connect
* Under Automatic deploys, click Enable Automatic Deploys


* Back in VS Code terminal :
```
$ pipenv install gunicorn
$ touch wsgi.py
```
* Inside wsgi.py :
```
from api import create_app

app = create_app()
```


```
$ touch Procfile
```
* Inside Procfile :
```
web: gunicorn wsgi:app
```
* Commit and push changes
* If not already automatically starting build and deploying:
* Under manual deploy, click Deploy Branch
* Once deployed, go to the deployed url by clicking Open app at the top of the page
* Should see Not Found because you haven't set up the root route at '/'
* If you navigate to '/api/items' you should see:
```
{
	items: [ ]
}
```
* just like it showed locally!


* On the Heroku app page, click Overview tab
* In Installed add-ons section, click Configure Add-ons
* In the Add-ons search bar, type postgres
* 'Heroku Postgres' should be available, click that
* Select Plan (Hobby Dev is free)
* Click Provision
* In Settings tab, under Config Vars, click reveal Config Vars
* Click the edit button
* Copy the value of the DATABASE_URL
* Exit edit screen


* In VS Code:
```
$ pipenv install python-dotenv
$ touch .env
```
* in .env :
```
DATABASE_URL=<copied db url value>
```
* in api/\_\_init\_\_.py
* Refactor the code to look like the following :
```
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
  app = Flask(__name__)
  
  # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

  db.init_app(app)

  from .views import api
  app.register_blueprint(api)

  return app
```


```
$ pipenv install psycopg2
```
* If that fails :
```
$ pipenv uninstall psycopg2
$ pipenv install psycopg2-binary
```


```
$ touch api/models.py
```
* inside api/models.py :
```
from . import db

class Item(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  description = db.Column(db.String(250))
```


* Before using Postgres let's set up a local sqlite db just for easy development purposes
* In the terminal, open the python shell by typing :
```
$ python
```
* then, type the following commands:
```
>>> from api.models import Item
>>> from api import db, create_app
>>> db.create_all(app=create_app())
```
* This should create a database.db file in the /api folder
* Back in the terminal, check to see if the table was created by entering the following :
```
$ sqlite3 api/database.db
```
* Now in the sqlite shell :
```
.tables
```
* You should see 'item'
* If you type 'select * from item', nothing should show up since there isn't anything in the db yet
* Type .exit to exit the sqlite shell


* In api/views.py, make the following changes :
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


```
$ flask run
```
* Open Postman
* Change method to POST and navigate to http://localhost:5000/api/add_item
* Click the Body tab
* Make sure the dropdown on the right is set to JSON
* Select 'raw' as the input type and enter something like :
```
{ 
	"name" : "Greg",
	"description" : "Learning how to build a flask/react app from scratch!"
}
```
* Click send
* Should receive the Done message if everything works out
* Back in VS Code terminal, type :
```
$ sqlite3 api/database.db
select * from item
```
* You should see your entry there!
* In api/views.py :
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
* Now in Postman, the /api/items get request should show the data you entered!


* Okay now we are going to get things up and running on your app deployed on heroku with the Postgres db
* First, in api/\_\_init\_\_.py, switch the commented-out lines :
```
…

  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
  # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

…
```
```
$ touch api/commands.py
```
* inside api/commands.py :
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
* Refactor api/\_\_init\_\_.py with the commands lines :
```
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .commands import reset_items

def create_app():
  app = Flask(__name__)

  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
  # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
  
  db.init_app(app)

  from .views import api
  app.register_blueprint(api)

  app.cli.add_command(reset_items)

  return app
```
* Git commit, push, and wait for Heroku to rebuild/redeploy
* In the heroku dashboard, click the 'More' dropdown in the top right corner
* Click run console
* Type 'flask reset_items' and then click Run
* Navigate to your deployed url + '/api/items'
* And you should see:
```
{
	items: [ ]
}
```
* Back in Heroku, you may need to add a SECRET_KEY as another config var, you can make it any random string that you would like (I am unsure if this is actually needed or not, since my other flask/react apps haven't needed one)
* If you want to reset on the local server side, type 'flask reset_items' and then 'flask run'


* You should be all set up to build out the React frontend now!


* in the VS terminal, keep the flask backend running on one terminal
* Open up a new terminal and type:
```
$ npx create-react-app react-frontend
$ cd react-frontend
$ npm start
```
* Open up a new terminal and type : 
```
$ cd react-frontend/
$ npm i semantic-ui-react semantic-ui-css
```
* In index.js, add this import to the rest of the imports:
```
import 'semantic-ui-css/semantic.min.css';
```
* In package.json, add the proxy as so:
```
…
  },
  "proxy": "http://localhost:5000",
  "browserslist": {
…
```
* In the terminal, make sure you are still in /react-frontend
* Do the following commands :
```
$ mkdir components
$ touch components/ItemForm.js
$ touch components/Items.js
```
* In ItemForm.js :
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
* In Items.js :
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
* Refactor App.js as so: 
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
* Delete the logo.svg file and README.md files
* In App.css :
```
.App {
  text-align: center;
}
```
* Git commit and git push - almost there!


* Now that we have a front end that we are happy with and don't anticipate needing the React hot-reloading much more, it's time to build this out to be served by our Flask backend.  Again, you will lose the handy React hot-reloading on localhost:3000 with npm start by using this method, so be sure to have your frontend in a relatively finished state before doing these final steps.  After these steps, you can still make changes to the frontend, but they must be applied manually with a terminal command and a small wait time.
* In the terminal :
```
$ mkdir api/static
$ mkdir api/templates
```
* In api/views.py, add a home route as such:
```
from flask import Blueprint, jsonify, request, render_template

…

@api.route('/')
def my_index():
  return render_template('index.html', token='Hello Flask+React')

…
```
* git commit and push before doing the following
* In the terminal :
```
$ cd react-frontend/
$ npm run eject
```
* When prompted to confirm, type y
* Once completed, in config/paths.js around line 72:
* Change appBuild to:
```
  appBuild: resolveApp('../api/static/react'),
```
* In web pack.config.js, control+F and command+D for 'static/' as necessary and erase them all, there should be around 8 of them
* Down around line ~528, in plugins: [ new HtmlWebpackPlugin( Object.assign etc, beneath the inject and template lines, write the following:
```
          filename: '../../templates/index.html',
```
* In public/index.html, underneath the <title> tag, write :
```
    <script>window.token = "{{ token }}"</script>
```
* In the react frontend, in App.js, can put the following anywhere you want to test if things are properly working :
```
      <p>My Token = { window.token }</p>
```
* In package.json, add a homepage top-level variable:
```
… 
  "private": true,
  "homepage": "/static/react",
  "dependencies": {
…
```
* making sure you are in the react frontend directory
* In the terminal, type :
```
npm run build
```
* Install any necessary packages that you are prompted to
* You should see a react folder in the api/static folder now and and index.html in the templates folder
* **Note:** Anytime you make any changes to your react frontend, you need to do 'npm run build' to update the actually served files inside the api directory
* Start up your flask backend
* Browse to localhost:5000
* You should see your react frontend with the sample token message!
* git commit and push and wait for Heroku to rebuild/redeploy


**Congrats, you made it to the end of this guide!**
**Check out your shiny new deployed Flask/React app!!!**

[Deployed Link!](https://flask-react-app-from-scratch.herokuapp.com/)

This app creation process was written out after completing the following code-alongs with Anthony Herbert (Pretty Printed), Ben Awad, and Joran Beasly: [Flask Movie API Example](https://youtu.be/Urx8Kj00zsI) | [How to Call a Flask API in React](https://youtu.be/06pWsB_hoD4) | [Deploy a Flask App to Heroku With a Postgres Database](https://youtu.be/FKy21FnjKS0) | [Serving React with a Flask Backend](https://youtu.be/YW8VG_U-m48)