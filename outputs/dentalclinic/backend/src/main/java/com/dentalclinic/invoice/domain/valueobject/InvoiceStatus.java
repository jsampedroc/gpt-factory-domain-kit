package com.dentalclinic.invoice.domain.valueobject;

import com.dentalclinic.domain.shared.ValueObject;

public class InvoiceStatus {

    private final String value;

    public InvoiceStatus(String value) {
        this.value = value;
    }

    public String getValue() { return this.value; }

}