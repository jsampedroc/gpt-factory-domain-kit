package com.preschoolmanagement.parent.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.util.Objects;

public record Address(
        @NotBlank(message = "Street cannot be blank")
        @Size(max = 255, message = "Street cannot exceed 255 characters")
        String street,

        @NotBlank(message = "City cannot be blank")
        @Size(max = 100, message = "City cannot exceed 100 characters")
        String city,

        @NotBlank(message = "State cannot be blank")
        @Size(max = 100, message = "State cannot exceed 100 characters")
        String state,

        @NotBlank(message = "Postal code cannot be blank")
        @Pattern(regexp = "^[A-Z0-9\\-\\s]+$", message = "Postal code must be alphanumeric and can contain hyphens or spaces")
        @Size(max = 20, message = "Postal code cannot exceed 20 characters")
        String postalCode
) implements ValueObject {

    public Address {
        Objects.requireNonNull(street, "Street cannot be null");
        Objects.requireNonNull(city, "City cannot be null");
        Objects.requireNonNull(state, "State cannot be null");
        Objects.requireNonNull(postalCode, "Postal code cannot be null");

        if (street.isBlank()) {
            throw new IllegalArgumentException("Street cannot be blank");
        }
        if (city.isBlank()) {
            throw new IllegalArgumentException("City cannot be blank");
        }
        if (state.isBlank()) {
            throw new IllegalArgumentException("State cannot be blank");
        }
        if (postalCode.isBlank()) {
            throw new IllegalArgumentException("Postal code cannot be blank");
        }
        if (street.length() > 255) {
            throw new IllegalArgumentException("Street cannot exceed 255 characters");
        }
        if (city.length() > 100) {
            throw new IllegalArgumentException("City cannot exceed 100 characters");
        }
        if (state.length() > 100) {
            throw new IllegalArgumentException("State cannot exceed 100 characters");
        }
        if (postalCode.length() > 20) {
            throw new IllegalArgumentException("Postal code cannot exceed 20 characters");
        }
        if (!postalCode.matches("^[A-Z0-9\\-\\s]+$")) {
            throw new IllegalArgumentException("Postal code must be alphanumeric and can contain hyphens or spaces");
        }
    }
}