package com.dentalclinic.treatment.domain.service;

import com.dentalclinic.domain.valueobject.Money;
import com.dentalclinic.treatment.domain.model.Treatment;
import com.dentalclinic.treatment.domain.repository.TreatmentRepository;
import java.util.UUID;

public class TreatmentDomainService {

    private final TreatmentRepository repository;

    public TreatmentDomainService(TreatmentRepository repository) {
        this.repository = repository;
    }

}
