package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.UUID;

@RestController
@RequestMapping("/api/insurance")
@Tag(name = "Insurance", description = "Patient insurance / convenio management")
public class InsuranceController {

    private final InsuranceRepository repository;

    public InsuranceController(InsuranceRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/patient/{patientId}")
    @Operation(summary = "Get insurance for a patient")
    public ResponseEntity<Insurance> getByPatient(@PathVariable UUID patientId) {
        return repository.findByPatientId(patientId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping("/patient/{patientId}")
    @Operation(summary = "Create or update insurance for a patient")
    public ResponseEntity<Insurance> upsert(
            @PathVariable UUID patientId,
            @RequestBody InsuranceRequest req) {
        Insurance insurance = repository.findByPatientId(patientId)
                .orElse(new Insurance(patientId, req.insuranceCompany(), req.policyNumber(),
                        req.coverageType(), req.coveragePercent(), req.validUntil(), req.notes()));
        return ResponseEntity.ok(repository.save(insurance));
    }

    public record InsuranceRequest(
            String insuranceCompany,
            String policyNumber,
            String coverageType,
            Integer coveragePercent,
            LocalDate validUntil,
            String notes) {}
}
