package com.preschoolmanagement.child.shared.application.dto;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

public class ChildResponse {

    private final UUID id;
    private final String firstName;
    private final String lastName;
    private final LocalDate birthDate;
    private final List<AllergyResponse> allergies;
    private final List<ImmunizationResponse> immunizations;
    private final List<AuthorizedPickupResponse> authorizedPickups;

    public ChildResponse(
            UUID id,
            String firstName,
            String lastName,
            LocalDate birthDate,
            List<AllergyResponse> allergies,
            List<ImmunizationResponse> immunizations,
            List<AuthorizedPickupResponse> authorizedPickups
    ) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.birthDate = birthDate;
        this.allergies = allergies;
        this.immunizations = immunizations;
        this.authorizedPickups = authorizedPickups;
    }

    public UUID id() {
        return id;
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

    public List<AllergyResponse> allergies() {
        return allergies;
    }

    public List<ImmunizationResponse> immunizations() {
        return immunizations;
    }

    public List<AuthorizedPickupResponse> authorizedPickups() {
        return authorizedPickups;
    }
}