package com.preschoolmanagement.child.shared.application.dto;

import jakarta.validation.constraints.NotBlank;
import java.time.LocalDate;

public class ImmunizationRequest {

    @NotBlank
    private String name;

    private LocalDate dateAdministered;

    public ImmunizationRequest() {
    }

    public ImmunizationRequest(String name, LocalDate dateAdministered) {
        this.name = name;
        this.dateAdministered = dateAdministered;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public LocalDate getDateAdministered() {
        return dateAdministered;
    }

    public void setDateAdministered(LocalDate dateAdministered) {
        this.dateAdministered = dateAdministered;
    }
}