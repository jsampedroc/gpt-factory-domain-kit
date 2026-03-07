package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotNull;
import java.util.Objects;

public record GeoLocation(@NotNull Double value) implements ValueObject {

    public GeoLocation {
        Objects.requireNonNull(value, "GeoLocation value cannot be null");
        // Add any specific validation for latitude/longitude ranges if needed.
        // Example: validateLatitudeLongitude(value);
    }

    // Optional: Add a helper method if you need to split into latitude/longitude later.
    // For now, it's a simple wrapper around a Double.
}