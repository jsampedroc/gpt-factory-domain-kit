package com.dentalclinic.patient.domain.service;

import com.dentalclinic.patient.domain.model.Patient;
import com.dentalclinic.patient.domain.repository.PatientRepository;
import java.time.LocalDate;
import java.util.UUID;

public class PatientDomainService {

    private final PatientRepository repository;

    public PatientDomainService(PatientRepository repository) {
        this.repository = repository;
    }

}
