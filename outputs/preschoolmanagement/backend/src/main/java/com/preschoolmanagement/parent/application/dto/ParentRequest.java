package com.preschoolmanagement.parent.application.dto;

import com.preschoolmanagement.parent.domain.valueobject.ParentRequestId;
import java.util.List;



public record ParentRequest(
        ParentRequestId id,
        String firstName,
        String lastName,
        String contactNumber,
        Address address,
        List<Child> children
) {}
