const Router = require('@koa/router');

const router = new Router();

router.get('/users', async (ctx) => {
  ctx.body = [];
});

router.post('/users', async (ctx) => {
  ctx.status = 201;
  ctx.body = { created: true };
});

router.get('/users/:id', async (ctx) => {
  ctx.body = { id: ctx.params.id };
});

router.delete('/users/:id', async (ctx) => {
  ctx.status = 204;
});

module.exports = router;
