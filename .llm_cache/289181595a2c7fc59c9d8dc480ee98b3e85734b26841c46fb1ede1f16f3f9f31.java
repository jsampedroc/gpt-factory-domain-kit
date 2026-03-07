package com.preschoolmanagement.child.shared.application.dto;

import jakarta.validation.constraints.NotBlank;

public class AllergyRequest {

    @NotBlank
    private String name;

    private String severity;

    public AllergyRequest(String name, String severity) {
        this.name = name;
        this.severity = severity;
    }

    public String name() {
        return name;
    }

    public String severity() {
        return severity;
    }
}