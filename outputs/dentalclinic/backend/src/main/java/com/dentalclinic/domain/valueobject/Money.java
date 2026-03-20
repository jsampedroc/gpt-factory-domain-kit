package com.dentalclinic.domain.valueobject;

import com.dentalclinic.domain.shared.ValueObject;

public class Money {

    private final Double amount;
    private final String currency;

    public Money(Double amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }

    public Double getAmount() { return this.amount; }

    public String getCurrency() { return this.currency; }

}