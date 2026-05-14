using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/health", () => Results.Ok(new { status = "healthy" }));

app.MapGet("/items", () => Results.Ok(new[] { "item1", "item2" }));

app.MapPost("/items", (CreateItemRequest req) =>
{
    return Results.Created($"/items/1", req);
});

app.MapGet("/items/{id}", (int id) => Results.Ok(new { id }));

app.MapPut("/items/{id}", (int id, UpdateItemRequest req) =>
{
    return Results.Ok(new { id, updated = true });
});

app.MapDelete("/items/{id}", (int id) =>
{
    return Results.NoContent();
});

app.Run();

record CreateItemRequest(string Name, decimal Price);
record UpdateItemRequest(string Name, decimal Price);
