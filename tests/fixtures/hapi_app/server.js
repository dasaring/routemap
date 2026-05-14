"use strict";

const Hapi = require("@hapi/hapi");

const init = async () => {
    const server = Hapi.server({
        port: 3000,
        host: "localhost",
    });

    server.route({
        method: "GET",
        path: "/users",
        handler: (request, h) => {
            return { users: [] };
        },
    });

    server.route({
        method: "POST",
        path: "/users",
        handler: (request, h) => {
            return h.response({ created: true }).code(201);
        },
    });

    server.route({
        method: "GET",
        path: "/users/{id}",
        handler: (request, h) => {
            return { id: request.params.id };
        },
    });

    server.route({
        method: ["PUT", "PATCH"],
        path: "/users/{id}",
        handler: (request, h) => {
            return { updated: true };
        },
    });

    server.route({
        method: "DELETE",
        path: "/users/{id}",
        handler: (request, h) => {
            return h.response().code(204);
        },
    });

    server.route({
        method: "GET",
        path: "/health",
        handler: (request, h) => {
            return { status: "ok" };
        },
    });

    await server.start();
    console.log("Server running on %s", server.info.uri);
};

process.on("unhandledRejection", (err) => {
    console.log(err);
    process.exit(1);
});

init();
