package com.preschoolmanagement.child.shared.application.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;
import java.util.List;

public class ChildRequest {

    @NotBlank
    private String firstName;

    @NotBlank
    private String lastName;

    @NotNull
    private LocalDate birthDate;

    @NotNull
    private List<AllergyRequest> allergies;

    @NotNull
    private List<ImmunizationRequest> immunizations;

    @NotNull
    private List<AuthorizedPickupRequest> authorizedPickups;

    public ChildRequest() {
    }

    public ChildRequest(String firstName, String lastName, LocalDate birthDate, List<AllergyRequest> allergies, List<ImmunizationRequest> immunizations, List<AuthorizedPickupRequest> authorizedPickups) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.birthDate = birthDate;
        this.allergies = allergies;
        this.immunizations = immunizations;
        this.authorizedPickups = authorizedPickups;
    }

    public String firstName() {
        return firstName;
    }

    public String lastName() {
        return lastName;
    }

    public LocalDate birthDate() {
        return birthDate;
    }

    public List<AllergyRequest> allergies() {
        return allergies;
    }

    public List<ImmunizationRequest> immunizations() {
        return immunizations;
    }

    public List<AuthorizedPickupRequest> authorizedPickups() {
        return authorizedPickups;
    }
}