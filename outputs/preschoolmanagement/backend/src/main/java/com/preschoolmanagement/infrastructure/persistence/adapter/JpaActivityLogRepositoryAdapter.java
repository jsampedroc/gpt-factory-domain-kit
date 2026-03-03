package com.preschoolmanagement.infrastructure.persistence.adapter;

import com.preschoolmanagement.domain.model.ActivityLog;
import com.preschoolmanagement.domain.repository.ActivityLogRepository;
import com.preschoolmanagement.domain.valueobject.ActivityLogId;
import com.preschoolmanagement.infrastructure.persistence.entity.ActivityLogJpaEntity;
import com.preschoolmanagement.infrastructure.persistence.spring.SpringDataActivityLogRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaActivityLogRepositoryAdapter implements ActivityLogRepository {

    private final SpringDataActivityLogRepository repo;

    public JpaActivityLogRepositoryAdapter(SpringDataActivityLogRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public ActivityLog save(ActivityLog activityLog) {
        ActivityLogJpaEntity entity = new ActivityLogJpaEntity(
                activityLog.id().value(),
                activityLog.activityType(),
                activityLog.description(),
                activityLog.userId(),
                activityLog.timestamp()
        );
        ActivityLogJpaEntity saved = repo.save(entity);
        return new ActivityLog(
                new ActivityLogId(saved.getId()),
                saved.getActivityType(),
                saved.getDescription(),
                saved.getUserId(),
                saved.getTimestamp()
        );
    }

    @Override
    public Optional<ActivityLog> findById(ActivityLogId id) {
        return repo.findById(id.value())
                .map(e -> new ActivityLog(
                        new ActivityLogId(e.getId()),
                        e.getActivityType(),
                        e.getDescription(),
                        e.getUserId(),
                        e.getTimestamp()
                ));
    }
}
