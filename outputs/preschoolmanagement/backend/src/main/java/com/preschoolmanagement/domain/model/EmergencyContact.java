package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.EmergencyContactId;

import java.util.Objects;

public class EmergencyContact extends Entity<EmergencyContactId> {

    private final String name;

    public EmergencyContact(EmergencyContactId id, String name) {
        super(id);
        this.name = Objects.requireNonNull(name);
    }

    public String name() {
        return name;
    }
}
