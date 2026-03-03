package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.ActivityLogId;


public class ActivityLog extends Entity<ActivityLogId> {

    public ActivityLog(ActivityLogId id) {
        super(id);
    }
}
