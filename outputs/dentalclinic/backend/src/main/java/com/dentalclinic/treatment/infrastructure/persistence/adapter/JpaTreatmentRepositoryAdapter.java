package com.dentalclinic.treatment.infrastructure.persistence.adapter;

import com.dentalclinic.shared.PageResult;
import com.dentalclinic.treatment.domain.model.Treatment;
import com.dentalclinic.treatment.domain.repository.TreatmentRepository;
import com.dentalclinic.treatment.domain.valueobject.TreatmentId;
import com.dentalclinic.treatment.infrastructure.persistence.entity.TreatmentJpaEntity;
import com.dentalclinic.treatment.infrastructure.persistence.spring.SpringDataTreatmentRepository;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Repository;
import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
public class JpaTreatmentRepositoryAdapter implements TreatmentRepository {

    private final SpringDataTreatmentRepository springRepository;

    public JpaTreatmentRepositoryAdapter(SpringDataTreatmentRepository springRepository) {
        this.springRepository = springRepository;
    }

    @Override
    public Treatment save(Treatment entity) {
        TreatmentJpaEntity jpa = toJpaEntity(entity);
        return toDomain(springRepository.save(jpa));
    }

    @Override
    public Optional<Treatment> findById(UUID id) {
        return springRepository.findById(id).map(this::toDomain);
    }

    @Override
    public PageResult<Treatment> findAll(int page, int size, String search) {
        Specification<TreatmentJpaEntity> spec = Specification.where(null);
        spec = spec.and((root, q, cb) -> cb.isFalse(root.get("deleted")));
        if (search != null && !search.isBlank()) {
            String like = "%" + search.toLowerCase() + "%";
            spec = spec.and((root, query, cb) -> cb.or(
                cb.like(cb.lower(root.get("title")), like),
                cb.like(cb.lower(root.get("description")), like)
            ));
        }

        var result = springRepository.findAll(spec, PageRequest.of(page, size));

        List<Treatment> content = result.getContent().stream()
                .map(this::toDomain)
                .collect(Collectors.toList());

        return new PageResult<>(content, result.getNumber(), result.getSize(), result.getTotalElements());
    }

    @Override
    public void deactivate(UUID id) {
        springRepository.findById(id).ifPresent(jpa -> {
            jpa.setDeleted(true);
            springRepository.save(jpa);
        });
    }

    private TreatmentJpaEntity toJpaEntity(Treatment domain) {
        TreatmentJpaEntity jpa = new TreatmentJpaEntity();
        jpa.setId(domain.getId().value());
        jpa.setClinicId(domain.getClinicId());
        jpa.setPatientId(domain.getPatientId());
        jpa.setPatientName(domain.getPatientName());
        jpa.setPractitionerId(domain.getPractitionerId());
        String title = domain.getTitle() != null ? domain.getTitle()
                : (domain.getDescription() != null ? domain.getDescription() : "Treatment Plan");
        jpa.setTitle(title);
        jpa.setDescription(domain.getDescription());
        jpa.setTotalAmount(domain.getTotalAmount() != null ? domain.getTotalAmount() : BigDecimal.ZERO);
        jpa.setStatus(domain.getStatus() != null ? domain.getStatus() : "DRAFT");
        jpa.setAcceptedDate(domain.getAcceptedDate());
        return jpa;
    }

    private Treatment toDomain(TreatmentJpaEntity jpa) {
        return new Treatment(
            new TreatmentId(jpa.getId()),
            jpa.getPatientId(),
            jpa.getPatientName(),
            jpa.getPractitionerId(),
            jpa.getTitle(),
            jpa.getDescription(),
            jpa.getTotalAmount(),
            jpa.getStatus(),
            jpa.getAcceptedDate(),
            jpa.getClinicId(),
            jpa.getCreatedAt()
        );
    }
}
