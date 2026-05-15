import { initTRPC } from '@trpc/server';

const t = initTRPC.create();

export const healthRouter = t.router({
  ping: t.procedure.query(async () => {
    return { status: 'ok', timestamp: new Date().toISOString() };
  }),

  version: t.procedure.query(async () => {
    return { version: '1.0.0' };
  }),
});
