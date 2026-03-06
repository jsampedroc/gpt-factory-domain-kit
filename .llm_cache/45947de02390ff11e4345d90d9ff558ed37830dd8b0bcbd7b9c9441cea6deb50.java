package com.preschoolmanagement.parent.application.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;
import java.util.List;
import com.preschoolmanagement.domain.model.Allergy;
import com.preschoolmanagement.domain.model.Immunization;
import com.preschoolmanagement.domain.model.AuthorizedPickup;

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

    public String getFirstName() {
        return firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public LocalDate getBirthDate() {
        return birthDate;
    }

    public List<Allergy> getAllergies() {
        return allergies;
    }

    public List<Immunization> getImmunizations() {
        return immunizations;
    }

    public List<AuthorizedPickup> getAuthorizedPickups() {
        return authorizedPickups;
    }
}