package com.preschoolmanagement.application.service;

import com.preschoolmanagement.domain.model.ActivityLog;
import com.preschoolmanagement.domain.repository.ActivityLogRepository;
import com.preschoolmanagement.domain.valueobject.ActivityLogId;

public class ActivityLogService {

    private final ActivityLogRepository repository;

    public ActivityLogService(ActivityLogRepository repository) {
        this.repository = repository;
    }

    public ActivityLog findById(ActivityLogId id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("ActivityLog not found"));
    }

    public void save(ActivityLog activityLog) {
        repository.save(activityLog);
    }
}
