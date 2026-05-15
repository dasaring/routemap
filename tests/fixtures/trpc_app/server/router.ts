import { initTRPC } from '@trpc/server';
import { z } from 'zod';

const t = initTRPC.create();

export const appRouter = t.router({
  listUsers: t.procedure.query(async () => {
    return [];
  }),

  getUser: t.procedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input }) => {
      return { id: input.id, name: 'Alice' };
    }),

  createUser: t.procedure
    .input(z.object({ name: z.string() }))
    .mutation(async ({ input }) => {
      return { id: '1', name: input.name };
    }),

  updateUser: t.procedure
    .input(z.object({ id: z.string(), name: z.string() }))
    .mutation(async ({ input }) => {
      return { id: input.id, name: input.name };
    }),

  deleteUser: t.procedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ input }) => {
      return { success: true };
    }),

  onUserUpdate: t.procedure
    .input(z.object({ id: z.string() }))
    .subscription(async function* ({ input }) {
      yield { id: input.id, event: 'updated' };
    }),
});

export type AppRouter = typeof appRouter;
