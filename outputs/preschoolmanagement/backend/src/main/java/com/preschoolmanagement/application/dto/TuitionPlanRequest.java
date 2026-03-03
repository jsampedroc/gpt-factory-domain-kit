package com.preschoolmanagement.application.dto;

public class TuitionPlanRequest {

    private String name;

    public TuitionPlanRequest(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}
