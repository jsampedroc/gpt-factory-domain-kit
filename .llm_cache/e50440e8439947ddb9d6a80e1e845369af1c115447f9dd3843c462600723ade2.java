package com.preschoolmanagement.child.shared.application.dto;

import java.time.LocalDate;

public class ImmunizationResponse {

    private final String name;
    private final LocalDate dateAdministered;

    public ImmunizationResponse(String name, LocalDate dateAdministered) {
        this.name = name;
        this.dateAdministered = dateAdministered;
    }

    public String name() {
        return name;
    }

    public LocalDate dateAdministered() {
        return dateAdministered;
    }
}