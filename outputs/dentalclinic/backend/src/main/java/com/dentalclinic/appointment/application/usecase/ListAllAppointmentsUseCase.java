package com.dentalclinic.appointment.application.usecase;

import com.dentalclinic.appointment.domain.model.Appointment;
import com.dentalclinic.appointment.domain.repository.AppointmentRepository;
import com.dentalclinic.shared.PageResult;
import org.springframework.stereotype.Service;

/**
 * Returns a paginated, searchable list of Appointment records
 */
@Service
public class ListAllAppointmentsUseCase {

    private final AppointmentRepository repository;

    public ListAllAppointmentsUseCase(AppointmentRepository repository) {
        this.repository = repository;
    }

    public PageResult<Appointment> execute(ListAllAppointmentsQuery query) {
        return repository.findAll(query.page(), query.size(), query.search());
    }
}
