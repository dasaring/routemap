import fastify, { FastifyInstance, FastifyPluginAsync } from 'fastify';

const app: FastifyInstance = fastify({ logger: true });

// Health check
app.get('/health', async (request, reply) => {
  return { status: 'ok' };
});

// Users routes
app.get('/users', async (request, reply) => {
  return { users: [] };
});

app.post('/users', async (request, reply) => {
  reply.code(201);
  return { created: true };
});

app.get('/users/:id', async (request, reply) => {
  return { user: null };
});

app.put('/users/:id', async (request, reply) => {
  return { updated: true };
});

app.delete('/users/:id', async (request, reply) => {
  reply.code(204);
  return {};
});

// Object-style route
app.route({
  method: 'GET',
  url: '/status',
  handler: async (request, reply) => {
    return { running: true };
  },
});

app.route({
  method: 'POST',
  url: '/items',
  handler: async (request, reply) => {
    reply.code(201);
    return { created: true };
  },
});

const start = async () => {
  try {
    await app.listen({ port: 3000 });
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
