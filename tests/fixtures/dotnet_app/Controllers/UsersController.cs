using Microsoft.AspNetCore.Mvc;

namespace MyApp.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    [HttpGet]
    public IActionResult GetAll()
    {
        return Ok(new[] { "alice", "bob" });
    }

    [HttpGet("{id}")]
    public IActionResult GetById(int id)
    {
        return Ok(new { id });
    }

    [HttpPost]
    public IActionResult Create([FromBody] CreateUserDto dto)
    {
        return CreatedAtAction(nameof(GetById), new { id = 1 }, dto);
    }

    [HttpPut("{id}")]
    public IActionResult Update(int id, [FromBody] CreateUserDto dto)
    {
        return Ok(new { id, updated = true });
    }

    [HttpDelete("{id}")]
    public IActionResult Delete(int id)
    {
        return NoContent();
    }
}

public record CreateUserDto(string Name, string Email);
