package com.dentalclinic.appointment.application.usecase;

import com.dentalclinic.appointment.domain.model.Appointment;
import com.dentalclinic.appointment.domain.repository.AppointmentRepository;
import com.dentalclinic.appointment.domain.valueobject.AppointmentId;
import com.dentalclinic.appointment.domain.valueobject.AppointmentStatus;
import java.util.UUID;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Caching;
import org.springframework.stereotype.Service;

/**
 * Updates an existing Appointment
 */
@Service
public class UpdateAppointmentUseCase {

    private final AppointmentRepository repository;

    public UpdateAppointmentUseCase(AppointmentRepository repository) {
        this.repository = repository;
    }

    @Caching(evict = {
        @CacheEvict(value = "entityById", key = "#command.appointmentId()"),
        @CacheEvict(value = "dashboard", allEntries = true)
    })
    public Appointment execute(UpdateAppointmentCommand command) {
        Appointment existing = repository.findById(command.appointmentId())
            .orElseThrow(() -> new IllegalArgumentException("Not found"));

        Appointment updated = new Appointment(
            new AppointmentId(command.appointmentId()),
            command.patientId() != null ? command.patientId() : existing.getPatientId(),
            command.patientName() != null ? command.patientName() : existing.getPatientName(),
            command.practitionerId() != null ? command.practitionerId() : existing.getPractitionerId(),
            command.practitionerName() != null ? command.practitionerName() : existing.getPractitionerName(),
            command.startTime() != null ? command.startTime() : existing.getStartTime(),
            command.endTime() != null ? command.endTime() : existing.getEndTime(),
            command.procedureName() != null ? command.procedureName() : existing.getProcedureName(),
            command.status() != null ? new AppointmentStatus(command.status())
                : existing.getStatus(),
            command.notes() != null ? command.notes() : existing.getNotes(),
            existing.getClinicId(),
            existing.getCreatedAt()
        );
        return repository.save(updated);
    }
}
