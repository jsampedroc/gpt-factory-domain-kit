package com.dentalclinic.appointment.application.usecase;

import com.dentalclinic.appointment.domain.model.Appointment;
import com.dentalclinic.appointment.domain.repository.AppointmentRepository;
import com.dentalclinic.appointment.domain.valueobject.AppointmentId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Caching;
import org.springframework.stereotype.Service;

/**
 * Deactivates a Appointment record
 */
@Service
public class DeactivateAppointmentUseCase {

    private final AppointmentRepository repository;

    public DeactivateAppointmentUseCase(AppointmentRepository repository) {
        this.repository = repository;
    }

    @Caching(evict = {
        @CacheEvict(value = "entityById", allEntries = true),
        @CacheEvict(value = "dashboard", allEntries = true)
    })
    public void execute(DeactivateAppointmentCommand command) {
        repository.deactivate(command.appointmentId());
    }
}