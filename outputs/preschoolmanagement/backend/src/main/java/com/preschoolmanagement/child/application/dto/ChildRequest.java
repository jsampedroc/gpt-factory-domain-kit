package com.preschoolmanagement.child.application.dto;

import com.preschoolmanagement.child.domain.valueobject.ChildRequestId;
import java.time.LocalDate;
import java.util.List;



public record ChildRequest(
        ChildRequestId id,
        String firstName,
        String lastName,
        LocalDate birthDate,
        List<Allergy> allergies,
        List<Immunization> immunizations,
        List<AuthorizedPickup> authorizedPickups
) {}
