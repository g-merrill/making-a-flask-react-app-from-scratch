## Setting Up Flask App and GitHub
1) Create your project repo on [Github](https://github.com/new)
2) 
```
$ mkdir flask-react-app
$ cd flask-react-app
$ git init && code .

$ virtualenv venv
$ source venv/bin/activate
$ pip install flask flask-sqlalchemy gunicorn python-dotenv psycopg2-binary

$ git add . && git status
$ git commit -m 'Initial commit'
$ git remote add origin https://github.com/<yourgithubusername>/<yourreponame>.git
$ git push -u origin master
```
3)
```
$ npx create-react-app app
$ touch app/__init__.py
```
4) inside \_\_init\_\_.py :
```
from flask import Flask

def create_app():
  app = Flask(__name__)

  return app
```
5)
```
$ touch .env
```
6) inside .env :
```
FLASK_APP=app
FLASK_DEBUG=1
```
7)
```
$ touch wsgi.py
```
8) inside wsgi.py :
```
from app import create_app
from dotenv import load_dotenv

load_dotenv()
app = create_app()
```
## Setting Up Initial Routes
9)
```
$ touch app/views.py
```
10) Inside views.py :
```
from flask import Blueprint, jsonify

api = Blueprint('api', __name__)

@api.route('/api/items')
def items():

  items = []

  return jsonify({ 'items': items })
```
11) inside \_\_init\_\_.py, modify the create_app function :
```
def create_app():
  app = Flask(__name__)

  from .views import api
  app.register_blueprint(api)

  return app
```
12) In the terminal :
```
$ flask run
```
13) Navigate to http://localhost:5000/api/items
* You should see :
```
{
  items: []
}
```
* __Note:__ Anytime that you close and reopen the terminal/project, you can get the app running locally in your virtual environment again with the following terminal commands :
```
$ source venv/bin/activate
$ flask run
```
* __Addtl Note:__ If you for some reason are getting 'command not found: flask' when attempting flask run, try reinstalling the python packages:
```
$ pip install flask flask-sqlalchemy gunicorn python-dotenv psycopg2-binary
```
14) Inside views.py, add the following function:
```
...

@api.route('/api/add_item', methods=['POST'])
def add_item():

  return 'The POST request to this route worked!', 201
```
15) Open [Postman](https://youtu.be/MdyJn4EKfc4)
16) Change method to POST and type http://localhost:5000/api/add_item as the request URL
17) Click the Body tab
* Make sure the dropdown on the right is set to JSON and 'raw' is selected as the input type
18) In the text area, enter something like :
```
{
  "test": "Expecting success message, and 201 response"
}
```
19) Click Send
* Postman should respond with what you wrote in views.py: "The POST request to this route worked!"
## Setting Up Heroku
20)
```
$ touch Procfile
```
21)  Inside Procfile :
```
web: gunicorn wsgi:app
```
22) Git commit and push changes
23) Open [Heroku](https://dashboard.heroku.com/) dashboard
24) new>Create new app
25) Give it a name and hit Create app
26) Under Deployment method, select GitHub
27) Connect to GitHub by searching for your repo
28) Once you have found the repo you are using, click Connect
29) Under Automatic deploys, click Enable Automatic Deploys
30) Under manual deploy, click Deploy Branch
31) Once deployed, navigate to the deployed url by clicking Open app at the top of the page
* It should give you a Not Found message because you haven't set up the root route at '/'
32) Navigate to your deployed url + '/api/items'
* You should see :
```
{
	items: [ ]
}
```
just like it showed locally!
## Setting Up Postgres via Heroku
33) On the Heroku app page, click Overview tab
34) In Installed add-ons section, click Configure Add-ons
35) In the Add-ons search bar, type 'postgres'
36) 'Heroku Postgres' should be available, click that
37) Select the plan you would like (Hobby Dev is free)
38) Click Provision
39) In Settings tab, under Config Vars, click reveal Config Vars
40) Click the edit button
41) Copy the value of the DATABASE_URL and exit, the string value should begin with 'postgres://'...
42) While you are there, add the FLASK_APP=app and FLASK_DEBUG=1 key-value pairs as additional Config Vars in the Heroku console
43) Back in VS Code, in the terminal :
```
$ pipenv install psycopg2-binary
```
44) in the .env file :
```
FLASK_APP=app
FLASK_DEBUG=1
DATABASE_URL=<copied db url value>
```
## Setting Up the Database Locally
45)
```
$ touch app/models.py
```
46) inside models.py :
```
from . import db

class Item(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  description = db.Column(db.String(250))
```
47)
```
$ touch app/commands.py
```
48) inside commands.py :
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
49) Refactor \_\_init\_\_.py as so :
```
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .commands import reset_items

def create_app():
  app = Flask(__name__)

  uri = os.getenv('DATABASE_URL')
  if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
  app.config['SQLALCHEMY_DATABASE_URI'] = uri
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  
  db.init_app(app)

  from .views import api
  app.register_blueprint(api)

  app.cli.add_command(reset_items)

  return app
```
50) In the terminal, type :
```
$ flask reset_items
```
* running this command should create the items table in your postgres db for the first time
## Item Create Route (The 'C' in CRUD)
51)  In views.py, make the following changes :
```
from flask import Blueprint, jsonify, request
from . import db
from .models import Item

...

@api.route('/api/add_item', methods=['POST'])
def add_item():
  item_data = request.get_json()

  new_item = Item(name=item_data['name'], description=item_data['description'])

  db.session.add(new_item)
  db.session.commit()

  return item_data, 201

...
```
52)
```
$ flask run
```
53) Open Postman
54) Change method to POST and type http://localhost:5000/api/add_item as the request URL
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
* Should receive the success message if everything works out
## Item Read-All Route (The 'R' in CRUD)
59)  In views.py :
```
...

@api.route('/api/items')
def items():
  items_list = Item.query.order_by(Item.id.desc())
  items = []

  for item in items_list:
    items.append({ 'name': item.name, 'description': item.description })

  return jsonify({ 'items': items })

...
```
60) In Postman, change the request method to GET
* __Note:__ While using Postman, remember to have your server running in the VS Code terminal via the 'flask run' command
61) Type 'http://localhost:5000/api/items' as the request URL
* Postman should show the JSON data you entered previously!
62) Git commit, push, and wait for Heroku to rebuild/redeploy
63) Navigate to your deployed url + '/api/items'
* You should also see the JSON data you entered in Postman!
* __Note:__ If you want to ever want to reset your database via the command line, type :
```
$ flask reset_items
```
## Set Up React Frontend
* You should be all set up to build out the React frontend now!
64) In package.json, add the proxy as so :
```
...

  },
  "proxy": "http://localhost:5000",
  "browserslist": {
...
```
* in the VS terminal, keep the flask backend running on one terminal
65)  Open up a new terminal and type :
```
$ cd app
$ npm start
```
* this should open up a browser window at http://localhost:3000
66) Open up another new terminal and type : 
```
$ cd app
$ npm i semantic-ui-react semantic-ui-css
```
67) In index.js, add this import to the rest of the imports :
```
...
import 'semantic-ui-css/semantic.min.css';
...
```
67b) There might be a [bug](https://github.com/Semantic-Org/Semantic-UI/issues/7073) with the semantic.min.css file, causing the npm start and build to fail to compile.  Do the following in package.json as a workaround:
```
...
  "scripts": {
    "start": "sed -i '' 's/;;/;/g' node_modules/semantic-ui-css/semantic.min.css && react-scripts start",
    "build": "sed -i '' 's/;;/;/g' node_modules/semantic-ui-css/semantic.min.css && react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
...
```
68) In the terminal, still inside the app directory :
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
71) Refactor App.js as so : 
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
## Serving the React build files with Flask
* Once we are happy with our React frontend, it's time to use 'npm run build' to serve the frontend files with our Flask backend.  However, for our Flask app to access the index.html created in the React build folder, we will need to do some nifty routing.
75)  In app/.gitignore, comment out the /build line, or just remove it completely :
```
...

# testing
/coverage

# # production
# /build

# misc
.DS_Store

...
```
76) in the terminal, type :
```
$ cd app
$ npm run build
```
77) refactor \_\_init\_\_.py :
```
import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .commands import reset_items

def create_app():
  app = Flask(__name__, static_folder='build')

  uri = os.getenv('DATABASE_URL')
  if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
  app.config['SQLALCHEMY_DATABASE_URI'] = uri

  db.init_app(app)

  from .views import api
  app.register_blueprint(api)

  # Serve React App
  @app.route('/', defaults={'path': ''})
  @app.route('/<path:path>')
  def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
      return send_from_directory(app.static_folder, path)
    else:
      return send_from_directory(app.static_folder, 'index.html')
  
  app.cli.add_command(reset_items)

  return app
```
78) With your backend still running on the first terminal session, browse once again to http://localhost:5000
* Now you should see your react frontend!
79) git commit, git push, wait for Heroku to rebuild/redeploy, open the app at the deployed url and...

**Check out your shiny new deployed Flask/React app!!!**
## Making Further Frontend Changes in React
80) Make any desired frontend changes
81) In the terminal :
```
$ git add . && git status
$ git commit -m 'Some description of changes'
$ cd app && npm run build && cd .. && open http://localhost:5000 && flask run
```
82) Git commit, push, and wait for Heroku to rebuild/redeploy
## Done!
**Congrats, you made it to the end of this guide!**

[Sample Deployed App!](https://flask-react-app-from-scratch.herokuapp.com/)

This app creation process was written out after completing the following code-alongs with Anthony Herbert (Pretty Printed), Ben Awad, and Joran Beasly: [Flask Movie API Example](https://youtu.be/Urx8Kj00zsI) | [How to Call a Flask API in React](https://youtu.be/06pWsB_hoD4) | [Deploy a Flask App to Heroku With a Postgres Database](https://youtu.be/FKy21FnjKS0) | [Serving React with a Flask Backend](https://youtu.be/YW8VG_U-m48)
