const express = require('express');
const router = express.Router();

// Get all users
router.get('/users', async (req, res) => {
  const users = await UserService.findAll();
  res.json(users);
});

// Get user by id
router.get('/users/:id', async (req, res) => {
  const user = await UserService.findById(req.params.id);
  if (!user) return res.status(404).json({ error: 'Not found' });
  res.json(user);
});

// Create user
router.post('/users', async (req, res) => {
  const user = await UserService.create(req.body);
  res.status(201).json(user);
});

// Update and delete via chained route
router.route('/users/:id')
  .put(async (req, res) => {
    const user = await UserService.update(req.params.id, req.body);
    res.json(user);
  })
  .patch(async (req, res) => {
    const user = await UserService.patch(req.params.id, req.body);
    res.json(user);
  })
  .delete(async (req, res) => {
    await UserService.delete(req.params.id);
    res.status(204).send();
  });

module.exports = router;
