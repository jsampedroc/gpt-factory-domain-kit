package com.preschoolmanagement.application.dto;

public class ActivityLogResponse {

    private final String id;
    private final String activityType;
    private final String description;
    private final String performedBy;
    private final String performedAt;

    public ActivityLogResponse(String id, String activityType, String description, String performedBy, String performedAt) {
        this.id = id;
        this.activityType = activityType;
        this.description = description;
        this.performedBy = performedBy;
        this.performedAt = performedAt;
    }

    public String getId() { return id; }
    public String getActivityType() { return activityType; }
    public String getDescription() { return description; }
    public String getPerformedBy() { return performedBy; }
    public String getPerformedAt() { return performedAt; }
}
