package com.dentalclinic.treatment.domain.repository;

import com.dentalclinic.shared.PageResult;
import com.dentalclinic.treatment.domain.model.Treatment;
import java.util.Optional;
import java.util.UUID;

public interface TreatmentRepository {

    Treatment save(Treatment entity);

    Optional<Treatment> findById(UUID id);

    PageResult<Treatment> findAll(int page, int size, String search);

    void deactivate(UUID id);

}
