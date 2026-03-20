package com.dentalclinic.invoice.domain.valueobject;

import com.dentalclinic.domain.shared.ValueObject;
import com.dentalclinic.invoice.domain.valueobject.InvoiceId;
import java.util.Objects;
import java.util.UUID;

public final class InvoiceId implements ValueObject {
    private final UUID value;

    public InvoiceId(UUID value) {
        this.value = Objects.requireNonNull(value, "InvoiceId value cannot be null");
    }

    public UUID value() {
        return value;
    }

    public static InvoiceId newId() {
        return new InvoiceId(UUID.randomUUID());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        InvoiceId invoiceId = (InvoiceId) o;
        return Objects.equals(value, invoiceId.value);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(value);
    }

    @Override
    public String toString() {
        return "InvoiceId{" +
                "value=" + value +
                '}';
    }
}
