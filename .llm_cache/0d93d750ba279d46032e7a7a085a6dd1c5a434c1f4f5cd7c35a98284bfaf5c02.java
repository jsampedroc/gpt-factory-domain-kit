package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotNull;
import java.util.Objects;

public record GeoLocation(@NotNull Double value) implements ValueObject {

    public GeoLocation {
        Objects.requireNonNull(value, "GeoLocation value cannot be null");
        // Add any specific validation for latitude/longitude ranges if needed.
        // Example: validate latitude (-90 to 90) and longitude (-180 to 180).
        // For simplicity, we assume a Double value is acceptable.
    }
}