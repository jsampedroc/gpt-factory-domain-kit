package com.dentalclinic.shared;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import java.time.LocalDate;
import java.util.UUID;

/**
 * Stores insurance/convenio data for a patient.
 * One patient can have at most one active insurance record.
 */
@Entity
@Table(name = "insurance")
public class Insurance {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "patient_id", nullable = false)
    private UUID patientId;

    @NotBlank
    @Column(name = "insurance_company", nullable = false, length = 128)
    private String insuranceCompany;

    @Column(name = "policy_number", length = 64)
    private String policyNumber;

    @Column(name = "coverage_type", length = 32)
    private String coverageType; // FULL | PARTIAL | DENTAL_ONLY | NONE

    @Min(0) @Max(100)
    @Column(name = "coverage_percent")
    private Integer coveragePercent;

    @Future
    @Column(name = "valid_until")
    private LocalDate validUntil;

    @Column(name = "notes", length = 500)
    private String notes;

    protected Insurance() {}

    public Insurance(UUID patientId, String insuranceCompany, String policyNumber,
                     String coverageType, Integer coveragePercent,
                     LocalDate validUntil, String notes) {
        this.patientId = patientId;
        this.insuranceCompany = insuranceCompany;
        this.policyNumber = policyNumber;
        this.coverageType = coverageType;
        this.coveragePercent = coveragePercent;
        this.validUntil = validUntil;
        this.notes = notes;
    }

    public UUID getId() { return id; }
    public UUID getPatientId() { return patientId; }
    public String getInsuranceCompany() { return insuranceCompany; }
    public String getPolicyNumber() { return policyNumber; }
    public String getCoverageType() { return coverageType; }
    public Integer getCoveragePercent() { return coveragePercent; }
    public LocalDate getValidUntil() { return validUntil; }
    public String getNotes() { return notes; }
}
