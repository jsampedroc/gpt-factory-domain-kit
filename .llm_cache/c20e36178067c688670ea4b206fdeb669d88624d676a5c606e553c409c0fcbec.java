package com.preschoolmanagement.child.shared.application.dto;

public class AllergyResponse {

    private final String name;
    private final String severity;

    public AllergyResponse(String name, String severity) {
        this.name = name;
        this.severity = severity;
    }

    public String name() { return name; }
    public String severity() { return severity; }
}