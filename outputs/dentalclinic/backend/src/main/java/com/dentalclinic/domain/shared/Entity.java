package com.dentalclinic.domain.shared;

import java.util.Objects;

public abstract class Entity<ID extends ValueObject> {

    protected final ID id;

    protected Entity(ID id) {
        this.id = Objects.requireNonNull(id);
    }

    public ID id() {
        return id;
    }

    public ID getId() {
        return id;
    }
}