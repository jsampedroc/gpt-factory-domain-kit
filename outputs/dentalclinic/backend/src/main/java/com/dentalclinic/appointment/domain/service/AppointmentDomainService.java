package com.dentalclinic.appointment.domain.service;

import com.dentalclinic.appointment.domain.model.Appointment;
import com.dentalclinic.appointment.domain.repository.AppointmentRepository;
import com.dentalclinic.appointment.domain.valueobject.AppointmentStatus;
import java.time.LocalDateTime;
import java.util.UUID;

public class AppointmentDomainService {

    private final AppointmentRepository repository;

    public AppointmentDomainService(AppointmentRepository repository) {
        this.repository = repository;
    }

}
