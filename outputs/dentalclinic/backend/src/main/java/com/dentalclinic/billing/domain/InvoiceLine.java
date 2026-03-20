package com.dentalclinic.billing.domain;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "bill_invoice_line")
public class InvoiceLine {
    @Id
    @Column(columnDefinition = "uuid")
    private UUID id = UUID.randomUUID();

    @Column(name = "description", nullable = false)
    private String description;

    @Column(name = "quantity", nullable = false)
    private int quantity = 1;

    @Column(name = "unit_price", precision = 10, scale = 2, nullable = false)
    private BigDecimal unitPrice;

    @Column(name = "discount_percent", precision = 5, scale = 2)
    private BigDecimal discountPercent = BigDecimal.ZERO;

    @Column(name = "total", precision = 10, scale = 2, nullable = false)
    private BigDecimal total;

    protected InvoiceLine() {}

    public InvoiceLine(String description, int quantity, BigDecimal unitPrice) {
        this.description = description;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
        this.total = unitPrice.multiply(BigDecimal.valueOf(quantity));
    }

    public UUID getId() { return id; }
    public String getDescription() { return description; }
    public int getQuantity() { return quantity; }
    public BigDecimal getUnitPrice() { return unitPrice; }
    public BigDecimal getDiscountPercent() { return discountPercent; }
    public BigDecimal getTotal() { return total; }
}
