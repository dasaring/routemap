import { Application, Router } from "https://deno.land/x/oak/mod.ts";

const router = new Router();

router
  .get("/users", (ctx) => {
    ctx.response.body = [];
  })
  .post("/users", (ctx) => {
    ctx.response.body = { id: 1 };
  })
  .get("/users/:id", (ctx) => {
    ctx.response.body = { id: ctx.params.id };
  })
  .put("/users/:id", (ctx) => {
    ctx.response.body = { updated: true };
  })
  .delete("/users/:id", (ctx) => {
    ctx.response.status = 204;
  });

router.get("/health", (ctx) => {
  ctx.response.body = { status: "ok" };
});

const app = new Application();
app.use(router.routes());
app.use(router.allowedMethods());

await app.listen({ port: 8000 });
