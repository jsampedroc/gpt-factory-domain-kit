package com.preschoolmanagement.application.dto;

public class TuitionPlanResponse {

    private final String id;
    private final String name;

    public TuitionPlanResponse(String id, String name) {
        this.id = id;
        this.name = name;
    }

    public String getId() { return id; }
    public String getName() { return name; }
}
