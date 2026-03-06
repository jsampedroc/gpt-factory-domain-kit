package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.Objects;

public record Address(
        @NotBlank(message = "Address value cannot be blank")
        @Size(max = 500, message = "Address value cannot exceed 500 characters")
        String value
) implements ValueObject {

    public Address {
        Objects.requireNonNull(value, "Address value cannot be null");
        if (value.isBlank()) {
            throw new IllegalArgumentException("Address value cannot be blank");
        }
        if (value.length() > 500) {
            throw new IllegalArgumentException("Address value cannot exceed 500 characters");
        }
    }
}