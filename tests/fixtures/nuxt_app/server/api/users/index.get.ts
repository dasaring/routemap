// Nuxt 3 server API route: GET /api/users
import { defineEventHandler } from 'h3';

export default defineEventHandler(async (event) => {
  const users = [
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' },
  ];
  return users;
});
