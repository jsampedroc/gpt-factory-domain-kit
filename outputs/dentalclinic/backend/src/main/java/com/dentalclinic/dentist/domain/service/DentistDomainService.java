package com.dentalclinic.dentist.domain.service;

import com.dentalclinic.dentist.domain.model.Dentist;
import com.dentalclinic.dentist.domain.repository.DentistRepository;
import java.util.UUID;

public class DentistDomainService {

    private final DentistRepository repository;

    public DentistDomainService(DentistRepository repository) {
        this.repository = repository;
    }

}
