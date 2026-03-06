package com.preschoolmanagement.child.application.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;
import java.util.List;
import com.preschoolmanagement.domain.allergy.Allergy;
import com.preschoolmanagement.domain.immunization.Immunization;
import com.preschoolmanagement.domain.authorizedpickup.AuthorizedPickup;

public class ChildRequest {

    @NotBlank
    private final String firstName;

    @NotBlank
    private final String lastName;

    @NotNull
    private final LocalDate birthDate;

    private final List<Allergy> allergies;

    private final List<Immunization> immunizations;

    private final List<AuthorizedPickup> authorizedPickups;

    public ChildRequest(
            String firstName,
            String lastName,
            LocalDate birthDate,
            List<Allergy> allergies,
            List<Immunization> immunizations,
            List<AuthorizedPickup> authorizedPickups) {
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