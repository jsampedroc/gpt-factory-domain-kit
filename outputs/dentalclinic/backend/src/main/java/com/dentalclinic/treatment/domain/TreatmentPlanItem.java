package com.dentalclinic.treatment.domain;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "treat_plan_item")
public class TreatmentPlanItem {
    @Id
    @Column(columnDefinition = "uuid")
    private UUID id = UUID.randomUUID();

    @Column(name = "procedure_code")
    private String procedureCode;

    @Column(name = "procedure_name", nullable = false)
    private String procedureName;

    @Column(name = "tooth_number")
    private String toothNumber;

    @Column(name = "quantity", nullable = false)
    private int quantity = 1;

    @Column(name = "unit_price", precision = 10, scale = 2)
    private BigDecimal unitPrice = BigDecimal.ZERO;

    @Column(name = "discount_percent")
    private BigDecimal discountPercent = BigDecimal.ZERO;

    @Column(name = "status")
    @Enumerated(EnumType.STRING)
    private TreatmentItemStatus status = TreatmentItemStatus.PENDING;

    protected TreatmentPlanItem() {}

    public TreatmentPlanItem(String procedureName, String toothNumber, int quantity, BigDecimal unitPrice) {
        this.procedureName = procedureName;
        this.toothNumber = toothNumber;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
    }

    public UUID getId() { return id; }
    public String getProcedureCode() { return procedureCode; }
    public void setProcedureCode(String procedureCode) { this.procedureCode = procedureCode; }
    public String getProcedureName() { return procedureName; }
    public void setProcedureName(String procedureName) { this.procedureName = procedureName; }
    public String getToothNumber() { return toothNumber; }
    public void setToothNumber(String toothNumber) { this.toothNumber = toothNumber; }
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
    public BigDecimal getUnitPrice() { return unitPrice; }
    public void setUnitPrice(BigDecimal unitPrice) { this.unitPrice = unitPrice; }
    public BigDecimal getDiscountPercent() { return discountPercent; }
    public void setDiscountPercent(BigDecimal discountPercent) { this.discountPercent = discountPercent; }
    public TreatmentItemStatus getStatus() { return status; }
    public void setStatus(TreatmentItemStatus status) { this.status = status; }

    public BigDecimal getTotal() {
        BigDecimal base = unitPrice.multiply(BigDecimal.valueOf(quantity));
        BigDecimal discount = base.multiply(discountPercent).divide(BigDecimal.valueOf(100));
        return base.subtract(discount);
    }
}
