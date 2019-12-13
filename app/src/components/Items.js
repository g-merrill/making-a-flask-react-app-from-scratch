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