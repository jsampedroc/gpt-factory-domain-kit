package com.example.application.dto;

import jakarta.validation.constraints.NotBlank;

public class ExampleRequest {

    @NotBlank
    private String name;

    public String getName() {
        return name;
    }
}