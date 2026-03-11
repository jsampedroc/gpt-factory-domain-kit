package com.preschoolmanagement.parent.application.dto;

import com.preschoolmanagement.parent.domain.valueobject.ParentResponseId;
import java.util.List;



public record ParentResponse(
        ParentResponseId id,
        String firstName,
        String lastName,
        String contactNumber,
        Address address,
        List<Child> children
) {}
