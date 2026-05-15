#[macro_use] extern crate rocket;

use rocket::serde::json::Json;
use rocket::serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct User {
    id: u64,
    name: String,
}

#[get("/users")]
fn list_users() -> &'static str {
    "[]"
}

#[post("/users")]
fn create_user() -> &'static str {
    "{}"
}

#[get("/users/<id>")]
fn get_user(id: u64) -> &'static str {
    "{}"
}

#[put("/users/<id>")]
fn update_user(id: u64) -> &'static str {
    "{}"
}

#[delete("/users/<id>")]
fn delete_user(id: u64) -> &'static str {
    ""
}

#[get("/health")]
fn health() -> &'static str {
    "ok"
}

#[launch]
fn rocket() -> _ {
    rocket::build().mount("/", routes![
        list_users, create_user, get_user, update_user, delete_user, health
    ])
}
