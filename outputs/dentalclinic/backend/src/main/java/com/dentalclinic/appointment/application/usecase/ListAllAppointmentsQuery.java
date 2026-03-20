package com.dentalclinic.appointment.application.usecase;

public record ListAllAppointmentsQuery(int page, int size, String search) {}
