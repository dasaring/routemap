# routemap

Static analyzer that generates visual API route maps from Express and FastAPI codebases.

---

## Installation

```bash
pip install routemap
```

## Usage

Point `routemap` at your project directory and it will parse your routes and generate an interactive visual map.

```bash
# Analyze a FastAPI project
routemap analyze ./my-fastapi-app

# Analyze an Express project
routemap analyze ./my-express-app --framework express

# Export as PNG or HTML
routemap analyze ./my-fastapi-app --output routes.html
```

**Example output:**

```
Detected 24 routes across 6 routers
  GET    /api/users
  POST   /api/users
  GET    /api/users/{id}
  DELETE /api/users/{id}
  GET    /api/products
  ...

Route map saved to → routes.html
```

## Supported Frameworks

- **FastAPI** (Python)
- **Express** (Node.js)

## Requirements

- Python 3.8+
- Node.js 14+ *(only required when analyzing Express projects)*

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)