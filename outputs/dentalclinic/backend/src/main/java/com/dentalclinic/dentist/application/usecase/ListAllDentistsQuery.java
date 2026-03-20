package com.dentalclinic.dentist.application.usecase;

public record ListAllDentistsQuery(int page, int size, String search) {}
