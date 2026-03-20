package com.dentalclinic.invoice.application.usecase;

public record ListAllInvoicesQuery(int page, int size, String search) {}
