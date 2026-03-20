package com.dentalclinic.patient.application.usecase;

public record ListAllPatientsQuery(int page, int size, String search) {}
