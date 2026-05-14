var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();

var app = builder.Build();

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));
app.MapGet("/items", () => Results.Ok(new List<string>()));
app.MapPost("/items", (Item item) => Results.Created("/items/1", item));
app.MapGet("/items/{id}", (int id) => Results.Ok(id));
app.MapPut("/items/{id}", (int id, Item item) => Results.Ok(item));
app.MapDelete("/items/{id}", (int id) => Results.NoContent());

app.MapControllers();

app.Run();

record Item(int Id, string Name);
