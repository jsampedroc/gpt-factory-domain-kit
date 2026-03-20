package com.dentalclinic.patient.infrastructure.persistence.adapter;

import com.dentalclinic.patient.domain.model.Patient;
import com.dentalclinic.patient.domain.repository.PatientRepository;
import com.dentalclinic.patient.domain.valueobject.PatientId;
import com.dentalclinic.patient.infrastructure.persistence.entity.PatientJpaEntity;
import com.dentalclinic.patient.infrastructure.persistence.spring.SpringDataPatientRepository;
import com.dentalclinic.shared.PageResult;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
public class JpaPatientRepositoryAdapter implements PatientRepository {

    private final SpringDataPatientRepository springRepository;

    public JpaPatientRepositoryAdapter(SpringDataPatientRepository springRepository) {
        this.springRepository = springRepository;
    }

    @Override
    public Patient save(Patient entity) {
        PatientJpaEntity jpa = toJpaEntity(entity);
        return toDomain(springRepository.save(jpa));
    }

    @Override
    public Optional<Patient> findById(UUID id) {
        return springRepository.findById(id).map(this::toDomain);
    }

    @Override
    public PageResult<Patient> findAll(int page, int size, String search) {
        Specification<PatientJpaEntity> spec = Specification.where(null);
        spec = spec.and((root, q, cb) -> cb.isFalse(root.get("deleted")));
        spec = spec.and((root, q, cb) -> cb.isTrue(root.get("active")));
        if (search != null && !search.isBlank()) {
            String like = "%" + search.toLowerCase() + "%";
            spec = spec.and((root, q, cb) -> cb.or(
                cb.like(cb.lower(root.get("firstName")), like),
                cb.like(cb.lower(root.get("lastName")), like),
                cb.like(cb.lower(root.get("fullName")), like)
            ));
        }
        var p = springRepository.findAll(spec, PageRequest.of(page, size));
        List<Patient> content = p.getContent().stream().map(this::toDomain).collect(Collectors.toList());
        return new PageResult<>(content, page, size, p.getTotalElements());
    }

    @Override
    public void deactivate(UUID id) {
        springRepository.findById(id).ifPresent(jpa -> {
            jpa.setActive(false);
            jpa.setDeleted(true);
            springRepository.save(jpa);
        });
    }

    private PatientJpaEntity toJpaEntity(Patient domain) {
        PatientJpaEntity jpa = new PatientJpaEntity();
        jpa.setId(domain.getId().value());
        jpa.setClinicId(domain.getClinicId());
        jpa.setFullName(domain.getFullName());
        jpa.setFirstName(domain.getFirstName());
        jpa.setLastName(domain.getLastName());
        jpa.setBirthDate(domain.getBirthDate());
        jpa.setDniNie(domain.getDniNie());
        jpa.setEmail(domain.getEmail());
        jpa.setPhone(domain.getPhone());
        jpa.setGender(domain.getGender());
        jpa.setBloodType(domain.getBloodType());
        jpa.setAddress(domain.getAddress());
        jpa.setCity(domain.getCity());
        jpa.setPostalCode(domain.getPostalCode());
        jpa.setNotes(domain.getNotes());
        jpa.setActive(domain.isActive());
        if (domain.getClinicalAlerts() != null) {
            jpa.setClinicalAlerts(domain.getClinicalAlerts());
        }
        return jpa;
    }

    private Patient toDomain(PatientJpaEntity jpa) {
        return new Patient(
            new PatientId(jpa.getId()),
            jpa.getFullName(),
            jpa.getFirstName(),
            jpa.getLastName(),
            jpa.getBirthDate(),
            jpa.getDniNie(),
            jpa.getEmail(),
            jpa.getPhone(),
            jpa.getGender(),
            jpa.getBloodType(),
            jpa.getAddress(),
            jpa.getCity(),
            jpa.getPostalCode(),
            jpa.getNotes(),
            jpa.isActive(),
            jpa.getClinicalAlerts(),
            jpa.getClinicId(),
            jpa.getCreatedAt()
        );
    }
}
