package com.example.application.dto;

public class ExampleResponse {

    private final String id;
    private final String name;

    public ExampleResponse(String id, String name) {
        this.id = id;
        this.name = name;
    }

    public String getId() { return id; }
    public String getName() { return name; }
}