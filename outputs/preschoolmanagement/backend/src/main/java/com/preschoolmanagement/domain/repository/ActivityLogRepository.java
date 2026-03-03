package com.preschoolmanagement.domain.repository;

import com.preschoolmanagement.domain.model.ActivityLog;
import com.preschoolmanagement.domain.valueobject.ActivityLogId;

import java.util.Optional;

public interface ActivityLogRepository {

    Optional<ActivityLog> findById(ActivityLogId id);

    void save(ActivityLog entity);
}
