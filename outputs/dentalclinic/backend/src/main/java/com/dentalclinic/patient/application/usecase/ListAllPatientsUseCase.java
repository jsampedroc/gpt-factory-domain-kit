package com.dentalclinic.patient.application.usecase;

import com.dentalclinic.patient.domain.model.Patient;
import com.dentalclinic.patient.domain.repository.PatientRepository;
import com.dentalclinic.patient.domain.valueobject.PatientId;
import com.dentalclinic.shared.PageResult;
import java.util.UUID;
import org.springframework.stereotype.Service;

/**
 * Returns all Patient records with pagination and search
 */
@Service
public class ListAllPatientsUseCase {

    private final PatientRepository repository;

    public ListAllPatientsUseCase(PatientRepository repository) {
        this.repository = repository;
    }

    public PageResult<Patient> execute(ListAllPatientsQuery query) {
        return repository.findAll(query.page(), query.size(), query.search());
    }
}
