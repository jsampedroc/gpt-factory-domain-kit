package com.dentalclinic.dentist.application.usecase;

import com.dentalclinic.dentist.domain.model.Dentist;
import com.dentalclinic.dentist.domain.repository.DentistRepository;
import com.dentalclinic.shared.PageResult;
import org.springframework.stereotype.Service;

@Service
public class ListAllDentistsUseCase {

    private final DentistRepository repository;

    public ListAllDentistsUseCase(DentistRepository repository) {
        this.repository = repository;
    }

    public PageResult<Dentist> execute(ListAllDentistsQuery query) {
        return repository.findAll(query.page(), query.size(), query.search());
    }
}
