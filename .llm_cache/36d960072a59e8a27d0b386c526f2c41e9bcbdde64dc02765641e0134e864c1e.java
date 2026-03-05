package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotNull;
import java.util.Objects;

public record GeoLocation(@NotNull Double value) implements ValueObject {

    public GeoLocation {
        Objects.requireNonNull(value, "GeoLocation value cannot be null");
        // Add any specific validation for Double value if needed (e.g., range checks)
        // For example, if latitude/longitude ranges are known:
        // if (value < -90.0 || value > 90.0) {
        //     throw new IllegalArgumentException("GeoLocation value must be between -90 and 90");
        // }
    }
}