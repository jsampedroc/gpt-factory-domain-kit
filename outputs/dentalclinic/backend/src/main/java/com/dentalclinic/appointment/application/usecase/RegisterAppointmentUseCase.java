package com.dentalclinic.appointment.application.usecase;

import com.dentalclinic.appointment.domain.model.Appointment;
import com.dentalclinic.appointment.domain.repository.AppointmentRepository;
import com.dentalclinic.appointment.domain.valueobject.AppointmentId;
import com.dentalclinic.appointment.domain.valueobject.AppointmentStatus;
import com.dentalclinic.shared.kernel.ClinicContext;
import java.util.UUID;
import com.dentalclinic.appointment.domain.event.AppointmentScheduledEvent;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.stereotype.Service;

/**
 * Registers a new Appointment in the system
 */
@Service
public class RegisterAppointmentUseCase {

    private final AppointmentRepository repository;
    private final ApplicationEventPublisher publisher;
    private final ClinicContext clinicContext;

    public RegisterAppointmentUseCase(AppointmentRepository repository,
                                       ApplicationEventPublisher publisher,
                                       ClinicContext clinicContext) {
        this.repository = repository;
        this.publisher = publisher;
        this.clinicContext = clinicContext;
    }

    @CacheEvict(value = "dashboard", allEntries = true)
    public Appointment execute(RegisterAppointmentCommand command) {
        Appointment appointment = new Appointment(
            new AppointmentId(UUID.randomUUID()),
            command.patientId(),
            command.patientName(),
            command.practitionerId(),
            command.practitionerName(),
            command.startTime(),
            command.endTime() != null ? command.endTime() : command.startTime().plusHours(1),
            command.procedureName(),
            new AppointmentStatus("BOOKED"),
            command.notes(),
            clinicContext.current(),
            null
        );
        publisher.publishEvent(AppointmentScheduledEvent.of(
            appointment.getId().value(),
            appointment.getPatientId(),
            appointment.getPractitionerId(),
            appointment.getStartTime()
        ));
        return repository.save(appointment);
    }
}
