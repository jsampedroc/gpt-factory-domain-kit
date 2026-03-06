package com.preschoolmanagement.child.application.dto;

import java.time.LocalDate;
import java.util.List;

public class ChildResponse {

    private final String firstName;
    private final String lastName;
    private final LocalDate birthDate;
    private final List<Allergy> allergies;
    private final List<Immunization> immunizations;
    private final List<AuthorizedPickup> authorizedPickups;

    public ChildResponse(
            String firstName,
            String lastName,
            LocalDate birthDate,
            List<Allergy> allergies,
            List<Immunization> immunizations,
            List<AuthorizedPickup> authorizedPickups
    ) {
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

    public List<Allergy> allergies() {
        return allergies;
    }

    public List<Immunization> immunizations() {
        return immunizations;
    }

    public List<AuthorizedPickup> authorizedPickups() {
        return authorizedPickups;
    }
}