const fastify = require('fastify')({ logger: true });

// Simple shorthand routes
fastify.get('/users', async (request, reply) => {
  return { users: [] };
});

fastify.post('/users', async (request, reply) => {
  const user = request.body;
  reply.code(201).send(user);
});

fastify.get('/users/:id', async (request, reply) => {
  return { id: request.params.id };
});

fastify.put('/users/:id', async (request, reply) => {
  return { updated: true };
});

fastify.delete('/users/:id', async (request, reply) => {
  reply.code(204).send();
});

// Object-style route definition
fastify.route({
  method: 'GET',
  url: '/health',
  handler: async (request, reply) => {
    return { status: 'ok' };
  },
});

fastify.route({
  method: 'POST',
  url: '/auth/login',
  handler: async (request, reply) => {
    return { token: 'abc123' };
  },
});

const start = async () => {
  try {
    await fastify.listen({ port: 3000 });
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
