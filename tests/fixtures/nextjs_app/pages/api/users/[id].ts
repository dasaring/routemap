import type { NextApiRequest, NextApiResponse } from 'next';

type User = {
  id: string;
  name: string;
  email: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<User | { message: string }>
) {
  const { id } = req.query;

  if (req.method === 'GET') {
    res.status(200).json({ id: id as string, name: 'Alice', email: 'alice@example.com' });
  } else if (req.method === 'PUT') {
    res.status(200).json({ id: id as string, ...req.body });
  } else if (req.method === 'DELETE') {
    res.status(204).end();
  } else {
    res.setHeader('Allow', ['GET', 'PUT', 'DELETE']);
    res.status(405).json({ message: `Method ${req.method} Not Allowed` });
  }
}
