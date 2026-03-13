package com.preschoolmanagement.child.application.dto;

import java.time.LocalDate;
import java.util.List;



public record ChildRequest(
        String firstName,
        String lastName,
        LocalDate birthDate,
        List<Allergy> allergies,
        List<Immunization> immunizations,
        List<AuthorizedPickup> authorizedPickups
) {}
