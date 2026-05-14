package main

import (
	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	// Health check
	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"status": "ok"})
	})

	// API v1 group
	v1 := app.Group("/api/v1")

	v1.Get("/users", listUsers)
	v1.Post("/users", createUser)
	v1.Get("/users/:id", getUser)
	v1.Put("/users/:id", updateUser)
	v1.Delete("/users/:id", deleteUser)

	v1.Get("/products", listProducts)
	v1.Post("/products", createProduct)

	app.Listen(":3000")
}

func listUsers(c *fiber.Ctx) error   { return nil }
func createUser(c *fiber.Ctx) error  { return nil }
func getUser(c *fiber.Ctx) error     { return nil }
func updateUser(c *fiber.Ctx) error  { return nil }
func deleteUser(c *fiber.Ctx) error  { return nil }
func listProducts(c *fiber.Ctx) error  { return nil }
func createProduct(c *fiber.Ctx) error { return nil }
