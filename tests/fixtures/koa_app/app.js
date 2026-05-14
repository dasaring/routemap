const Koa = require('koa');
const Router = require('koa-router');

const app = new Koa();
const router = new Router();

// List all items
router.get('/items', async (ctx) => {
  ctx.body = { items: [] };
});

// Get single item
router.get('/items/:id', async (ctx) => {
  ctx.body = { id: ctx.params.id };
});

// Create item
router.post('/items', async (ctx) => {
  ctx.body = { created: true };
});

// Update item
router.put('/items/:id', async (ctx) => {
  ctx.body = { updated: true };
});

// Partial update
router.patch('/items/:id', async (ctx) => {
  ctx.body = { patched: true };
});

// Delete item
router.del('/items/:id', async (ctx) => {
  ctx.body = { deleted: true };
});

app.use(router.routes());
app.use(router.allowedMethods());

module.exports = app;
