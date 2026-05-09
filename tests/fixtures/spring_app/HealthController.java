package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;

@RestController
public class HealthController {

    @GetMapping("/health")
    public String health() {
        return "ok";
    }

    @GetMapping("/version")
    public String version() {
        return "1.0.0";
    }
}
