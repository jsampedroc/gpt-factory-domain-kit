package com.dentalclinic.treatment.application.usecase;

import com.dentalclinic.shared.PageResult;
import com.dentalclinic.treatment.domain.model.Treatment;
import com.dentalclinic.treatment.domain.repository.TreatmentRepository;
import org.springframework.stereotype.Service;

/**
 * Returns a paginated, searchable list of Treatment records.
 */
@Service
public class ListAllTreatmentsUseCase {

    private final TreatmentRepository repository;

    public ListAllTreatmentsUseCase(TreatmentRepository repository) {
        this.repository = repository;
    }

    public PageResult<Treatment> execute(ListAllTreatmentsQuery query) {
        return repository.findAll(query.page(), query.size(), query.search());
    }
}
