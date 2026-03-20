package com.dentalclinic.appointment.domain.repository;

import com.dentalclinic.appointment.domain.model.Appointment;
import com.dentalclinic.shared.PageResult;
import java.util.Optional;
import java.util.UUID;

public interface AppointmentRepository {

    Appointment save(Appointment entity);

    Optional<Appointment> findById(UUID id);

    PageResult<Appointment> findAll(int page, int size, String search);

    void deactivate(UUID id);

}
