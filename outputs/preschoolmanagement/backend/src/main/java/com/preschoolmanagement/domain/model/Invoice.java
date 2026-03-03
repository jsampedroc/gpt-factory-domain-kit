package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.InvoiceId;


public class Invoice extends Entity<InvoiceId> {

    public Invoice(InvoiceId id) {
        super(id);
    }
}
