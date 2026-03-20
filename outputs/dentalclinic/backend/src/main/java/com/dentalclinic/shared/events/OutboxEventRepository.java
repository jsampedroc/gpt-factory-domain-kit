package com.dentalclinic.shared.events;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface OutboxEventRepository extends JpaRepository<OutboxEvent, UUID> {
    List<OutboxEvent> findByPublishedFalseOrderByCreatedAtAsc();
}
