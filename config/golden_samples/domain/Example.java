package com.example.domain.model;

import com.example.domain.shared.Entity;
import com.example.domain.valueobject.ExampleId;

import java.util.Objects;

public class Example extends Entity<ExampleId> {

    private final String name;

    public Example(ExampleId id, String name) {
        super(id);
        this.name = Objects.requireNonNull(name);
    }

    public String name() {
        return name;
    }
}