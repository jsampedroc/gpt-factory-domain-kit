package com.dentalclinic.treatment.application.usecase;

import com.dentalclinic.treatment.domain.model.Treatment;
import com.dentalclinic.treatment.domain.repository.TreatmentRepository;
import com.dentalclinic.treatment.domain.valueobject.TreatmentId;
import com.dentalclinic.shared.kernel.ClinicContext;
import java.math.BigDecimal;
import java.util.UUID;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.stereotype.Service;

/**
 * Registers a new Treatment in the system
 */
@Service
public class RegisterTreatmentUseCase {

    private final TreatmentRepository repository;
    private final ClinicContext clinicContext;

    public RegisterTreatmentUseCase(TreatmentRepository repository, ClinicContext clinicContext) {
        this.repository = repository;
        this.clinicContext = clinicContext;
    }

    @CacheEvict(value = "dashboard", allEntries = true)
    public Treatment execute(RegisterTreatmentCommand command) {
        BigDecimal total = command.cost() != null
                ? BigDecimal.valueOf(command.cost().getAmount()) : BigDecimal.ZERO;

        Treatment treatment = new Treatment(
            new TreatmentId(UUID.randomUUID()),
            null,
            null,
            null,
            command.description() != null ? command.description() : "Treatment Plan",
            command.description(),
            total,
            "DRAFT",
            null,
            clinicContext.current(),
            null
        );
        return repository.save(treatment);
    }
}
