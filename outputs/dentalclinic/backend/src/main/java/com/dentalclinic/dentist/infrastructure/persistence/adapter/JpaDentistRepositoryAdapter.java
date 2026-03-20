package com.dentalclinic.dentist.infrastructure.persistence.adapter;

import com.dentalclinic.dentist.domain.model.Dentist;
import com.dentalclinic.dentist.domain.repository.DentistRepository;
import com.dentalclinic.dentist.domain.valueobject.DentistId;
import com.dentalclinic.dentist.infrastructure.persistence.entity.DentistJpaEntity;
import com.dentalclinic.dentist.infrastructure.persistence.spring.SpringDataDentistRepository;
import com.dentalclinic.shared.PageResult;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
public class JpaDentistRepositoryAdapter implements DentistRepository {

    private final SpringDataDentistRepository springRepository;

    public JpaDentistRepositoryAdapter(SpringDataDentistRepository springRepository) {
        this.springRepository = springRepository;
    }

    @Override
    public Dentist save(Dentist entity) {
        DentistJpaEntity jpa = toJpaEntity(entity);
        return toDomain(springRepository.save(jpa));
    }

    @Override
    public Optional<Dentist> findById(UUID id) {
        return springRepository.findById(id).map(this::toDomain);
    }

    @Override
    public PageResult<Dentist> findAll(int page, int size, String search) {
        Specification<DentistJpaEntity> spec = Specification.where(null);
        spec = spec.and((root, q, cb) -> cb.isTrue(root.get("active")));
        if (search != null && !search.isBlank()) {
            String like = "%" + search.toLowerCase() + "%";
            spec = spec.and((root, q, cb) -> cb.or(
                cb.like(cb.lower(root.get("firstName")), like),
                cb.like(cb.lower(root.get("lastName")), like),
                cb.like(cb.lower(root.get("licenseNumber")), like)
            ));
        }
        var p = springRepository.findAll(spec, PageRequest.of(page, size));
        List<Dentist> content = p.getContent().stream().map(this::toDomain).collect(Collectors.toList());
        return new PageResult<>(content, page, size, p.getTotalElements());
    }

    @Override
    public void deactivate(UUID id) {
        springRepository.findById(id).ifPresent(jpa -> {
            jpa.setActive(false);
            springRepository.save(jpa);
        });
    }

    private DentistJpaEntity toJpaEntity(Dentist domain) {
        DentistJpaEntity jpa = new DentistJpaEntity();
        jpa.setId(domain.getId().value());
        jpa.setFirstName(domain.getFirstName());
        jpa.setLastName(domain.getLastName());
        jpa.setLicenseNumber(domain.getLicenseNumber());
        jpa.setDentistId(domain.getDentistId());
        return jpa;
    }

    private Dentist toDomain(DentistJpaEntity jpa) {
        return new Dentist(
            new DentistId(jpa.getId()),
            jpa.getFirstName(),
            jpa.getLastName(),
            jpa.getLicenseNumber(),
            jpa.getDentistId()
        );
    }
}
