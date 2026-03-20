package com.dentalclinic.appointment.application.usecase;

import com.dentalclinic.appointment.domain.model.Appointment;
import com.dentalclinic.appointment.domain.repository.AppointmentRepository;
import com.dentalclinic.appointment.domain.valueobject.AppointmentId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

/**
 * Retrieves a Appointment by its identifier
 */
@Service
public class GetAppointmentByIdUseCase {

    private final AppointmentRepository repository;

    public GetAppointmentByIdUseCase(AppointmentRepository repository) {
        this.repository = repository;
    }

    @Cacheable(value = "entityById", key = "#query.appointmentId()")
    public Optional<Appointment> execute(GetAppointmentByIdQuery query) {
        return repository.findById(query.appointmentId());
    }
}