package com.preschoolmanagement.application.dto;

public class TeacherResponse {

    private final String id;
    private final String name;

    public TeacherResponse(String id, String name) {
        this.id = id;
        this.name = name;
    }

    public String getId() { return id; }
    public String getName() { return name; }
}
