package com.dentalclinic.appointment.infrastructure.persistence.adapter;

import com.dentalclinic.appointment.domain.model.Appointment;
import com.dentalclinic.appointment.domain.repository.AppointmentRepository;
import com.dentalclinic.appointment.domain.valueobject.AppointmentId;
import com.dentalclinic.appointment.domain.valueobject.AppointmentStatus;
import com.dentalclinic.appointment.infrastructure.persistence.entity.AppointmentJpaEntity;
import com.dentalclinic.appointment.infrastructure.persistence.spring.SpringDataAppointmentRepository;
import com.dentalclinic.shared.PageResult;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
public class JpaAppointmentRepositoryAdapter implements AppointmentRepository {

    private final SpringDataAppointmentRepository springRepository;

    public JpaAppointmentRepositoryAdapter(SpringDataAppointmentRepository springRepository) {
        this.springRepository = springRepository;
    }

    @Override
    public Appointment save(Appointment entity) {
        AppointmentJpaEntity jpa = toJpaEntity(entity);
        return toDomain(springRepository.save(jpa));
    }

    @Override
    public Optional<Appointment> findById(UUID id) {
        return springRepository.findById(id).map(this::toDomain);
    }

    @Override
    public PageResult<Appointment> findAll(int page, int size, String search) {
        Specification<AppointmentJpaEntity> spec = Specification.where(null);
        spec = spec.and((root, q, cb) -> cb.isFalse(root.get("deleted")));
        if (search != null && !search.isBlank()) {
            String like = "%" + search.toLowerCase() + "%";
            spec = spec.and((root, q, cb) -> cb.like(cb.lower(root.get("status")), like));
        }

        var result = springRepository.findAll(spec, PageRequest.of(page, size));
        List<Appointment> content = result.getContent().stream().map(this::toDomain).collect(Collectors.toList());
        return new PageResult<>(content, page, size, result.getTotalElements());
    }

    @Override
    public void deactivate(UUID id) {
        springRepository.findById(id).ifPresent(jpa -> {
            jpa.setDeleted(true);
            springRepository.save(jpa);
        });
    }

    private AppointmentJpaEntity toJpaEntity(Appointment domain) {
        AppointmentJpaEntity jpa = new AppointmentJpaEntity();
        jpa.setId(domain.getId().value());
        jpa.setClinicId(domain.getClinicId());
        jpa.setPatientId(domain.getPatientId());
        jpa.setPatientName(domain.getPatientName());
        jpa.setPractitionerId(domain.getPractitionerId());
        jpa.setPractitionerName(domain.getPractitionerName());
        jpa.setStartTime(domain.getStartTime());
        jpa.setEndTime(domain.getEndTime() != null ? domain.getEndTime()
                : (domain.getStartTime() != null ? domain.getStartTime().plusHours(1) : null));
        jpa.setProcedureName(domain.getProcedureName());
        jpa.setStatus(domain.getStatus() != null ? domain.getStatus().getValue() : "BOOKED");
        jpa.setNotes(domain.getNotes());
        return jpa;
    }

    private Appointment toDomain(AppointmentJpaEntity jpa) {
        return new Appointment(
            new AppointmentId(jpa.getId()),
            jpa.getPatientId(),
            jpa.getPatientName(),
            jpa.getPractitionerId(),
            jpa.getPractitionerName(),
            jpa.getStartTime(),
            jpa.getEndTime(),
            jpa.getProcedureName(),
            new AppointmentStatus(jpa.getStatus()),
            jpa.getNotes(),
            jpa.getClinicId(),
            jpa.getCreatedAt()
        );
    }
}
