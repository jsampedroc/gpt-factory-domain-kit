package com.dentalclinic.shared;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "treatment_plan_items")
public class TreatmentPlanItem {

    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @NotNull @Column(name = "plan_id", nullable = false)
    private UUID planId;

    @Column(name = "tooth_number")
    private Integer toothNumber;

    @NotBlank @Column(name = "procedure_code", length = 32)
    private String procedureCode;

    @NotBlank @Column(name = "description", length = 255)
    private String description;

    @Positive @Column(name = "quantity")
    private Integer quantity = 1;

    @NotNull @Column(name = "unit_price", precision = 10, scale = 2)
    private BigDecimal unitPrice;

    @Column(name = "total_price", precision = 10, scale = 2)
    private BigDecimal totalPrice;

    @Column(name = "insurance_coverage", precision = 10, scale = 2)
    private BigDecimal insuranceCoverage = BigDecimal.ZERO;

    /** PENDING | ACCEPTED | COMPLETED | CANCELLED */
    @Column(name = "status", length = 16)
    private String status = "PENDING";

    protected TreatmentPlanItem() {}

    public TreatmentPlanItem(UUID planId, Integer toothNumber, String procedureCode,
                              String description, Integer quantity, BigDecimal unitPrice,
                              BigDecimal insuranceCoverage) {
        this.planId = planId;
        this.toothNumber = toothNumber;
        this.procedureCode = procedureCode;
        this.description = description;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
        this.totalPrice = unitPrice.multiply(BigDecimal.valueOf(quantity));
        this.insuranceCoverage = insuranceCoverage != null ? insuranceCoverage : BigDecimal.ZERO;
    }

    public UUID getId() { return id; }
    public UUID getPlanId() { return planId; }
    public Integer getToothNumber() { return toothNumber; }
    public String getProcedureCode() { return procedureCode; }
    public String getDescription() { return description; }
    public Integer getQuantity() { return quantity; }
    public BigDecimal getUnitPrice() { return unitPrice; }
    public BigDecimal getTotalPrice() { return totalPrice; }
    public BigDecimal getInsuranceCoverage() { return insuranceCoverage; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
