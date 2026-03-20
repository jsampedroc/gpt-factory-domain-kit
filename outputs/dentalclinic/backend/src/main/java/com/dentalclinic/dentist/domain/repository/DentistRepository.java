package com.dentalclinic.dentist.domain.repository;

import com.dentalclinic.dentist.domain.model.Dentist;
import com.dentalclinic.shared.PageResult;
import java.util.Optional;
import java.util.UUID;

public interface DentistRepository {
    Dentist save(Dentist entity);
    Optional<Dentist> findById(UUID id);
    PageResult<Dentist> findAll(int page, int size, String search);

    void deactivate(UUID id);
}
