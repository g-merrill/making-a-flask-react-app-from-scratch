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
        onNewItem={item => setItems(currentItems => [item, ...currentItems])}
      />
      <p>My Token = { window.token }</p>
      <Items 
        items={ items }
      />
    </Container>
  );
}

export default App;
