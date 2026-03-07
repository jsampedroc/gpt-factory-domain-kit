package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.util.Objects;

public final class Address implements ValueObject {

    private final String street;
    private final String city;
    private final String state;
    private final String postalCode;

    public Address(
            @NotBlank(message = "Street cannot be blank") String street,
            @NotBlank(message = "City cannot be blank") String city,
            @NotBlank(message = "State cannot be blank") String state,
            @NotBlank(message = "Postal code cannot be blank")
            @Pattern(regexp = "^[0-9]{5}(-[0-9]{4})?$", message = "Postal code must be a valid US ZIP code")
            String postalCode) {
        this.street = Objects.requireNonNull(street, "Street cannot be null");
        this.city = Objects.requireNonNull(city, "City cannot be null");
        this.state = Objects.requireNonNull(state, "State cannot be null");
        this.postalCode = Objects.requireNonNull(postalCode, "Postal code cannot be null");

        if (this.street.isBlank()) {
            throw new IllegalArgumentException("Street cannot be blank");
        }
        if (this.city.isBlank()) {
            throw new IllegalArgumentException("City cannot be blank");
        }
        if (this.state.isBlank()) {
            throw new IllegalArgumentException("State cannot be blank");
        }
        if (this.postalCode.isBlank()) {
            throw new IllegalArgumentException("Postal code cannot be blank");
        }
        if (!this.postalCode.matches("^[0-9]{5}(-[0-9]{4})?$")) {
            throw new IllegalArgumentException("Postal code must be a valid US ZIP code");
        }
    }

    public String street() {
        return street;
    }

    public String city() {
        return city;
    }

    public String state() {
        return state;
    }

    public String postalCode() {
        return postalCode;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Address address = (Address) o;
        return Objects.equals(street, address.street) &&
                Objects.equals(city, address.city) &&
                Objects.equals(state, address.state) &&
                Objects.equals(postalCode, address.postalCode);
    }

    @Override
    public int hashCode() {
        return Objects.hash(street, city, state, postalCode);
    }

    @Override
    public String toString() {
        return "Address[" +
                "street=" + street + ", " +
                "city=" + city + ", " +
                "state=" + state + ", " +
                "postalCode=" + postalCode + ']';
    }
}