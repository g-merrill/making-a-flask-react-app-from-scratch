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