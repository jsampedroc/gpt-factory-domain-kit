package com.dentalclinic.shared;

public record DashboardStats(
    long totalPatients,
    long totalDentists,
    long totalAppointments,
    long totalTreatments,
    long totalInvoices
) {}
