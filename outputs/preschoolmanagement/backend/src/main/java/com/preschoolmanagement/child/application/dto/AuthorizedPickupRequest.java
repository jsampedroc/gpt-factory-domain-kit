package com.preschoolmanagement.child.application.dto;

public record AuthorizedPickupRequest(
        String firstName,
        String lastName,
        String relationshipToChild
) {}
