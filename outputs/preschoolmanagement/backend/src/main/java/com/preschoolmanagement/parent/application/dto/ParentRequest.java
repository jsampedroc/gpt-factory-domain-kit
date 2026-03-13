package com.preschoolmanagement.parent.application.dto;

import java.util.List;



public record ParentRequest(
        String firstName,
        String lastName,
        List<Child> children
) {}
