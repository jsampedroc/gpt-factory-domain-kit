package com.preschoolmanagement.infrastructure.persistence.adapter;

import com.preschoolmanagement.domain.model.EmergencyContact;
import com.preschoolmanagement.domain.repository.EmergencyContactRepository;
import com.preschoolmanagement.domain.valueobject.EmergencyContactId;
import com.preschoolmanagement.infrastructure.persistence.entity.EmergencyContactJpaEntity;
import com.preschoolmanagement.infrastructure.persistence.spring.SpringDataEmergencyContactRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaEmergencyContactRepositoryAdapter implements EmergencyContactRepository {

    private final SpringDataEmergencyContactRepository repo;

    public JpaEmergencyContactRepositoryAdapter(SpringDataEmergencyContactRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public EmergencyContact save(EmergencyContact emergencyContact) {
        EmergencyContactJpaEntity entity = new EmergencyContactJpaEntity(
                emergencyContact.id().value(),
                emergencyContact.name(),
                emergencyContact.relationship(),
                emergencyContact.phoneNumber()
        );
        EmergencyContactJpaEntity saved = repo.save(entity);
        return new EmergencyContact(
                new EmergencyContactId(saved.getId()),
                saved.getName(),
                saved.getRelationship(),
                saved.getPhoneNumber()
        );
    }

    @Override
    public Optional<EmergencyContact> findById(EmergencyContactId id) {
        return repo.findById(id.value())
                .map(e -> new EmergencyContact(
                        new EmergencyContactId(e.getId()),
                        e.getName(),
                        e.getRelationship(),
                        e.getPhoneNumber()
                ));
    }
}
