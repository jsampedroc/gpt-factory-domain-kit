package com.dentalclinic.config;

import com.dentalclinic.shared.DashboardStats;
import com.dentalclinic.patient.infrastructure.persistence.spring.SpringDataPatientRepository;
import com.dentalclinic.dentist.infrastructure.persistence.spring.SpringDataDentistRepository;
import com.dentalclinic.appointment.infrastructure.persistence.spring.SpringDataAppointmentRepository;
import com.dentalclinic.treatment.infrastructure.persistence.spring.SpringDataTreatmentRepository;
import com.dentalclinic.invoice.infrastructure.persistence.spring.SpringDataInvoiceRepository;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class DashboardService {

    private final SpringDataPatientRepository patientRepo;
    private final SpringDataDentistRepository dentistRepo;
    private final SpringDataAppointmentRepository appointmentRepo;
    private final SpringDataTreatmentRepository treatmentRepo;
    private final SpringDataInvoiceRepository invoiceRepo;

    public DashboardService(
            SpringDataPatientRepository patientRepo,
            SpringDataDentistRepository dentistRepo,
            SpringDataAppointmentRepository appointmentRepo,
            SpringDataTreatmentRepository treatmentRepo,
            SpringDataInvoiceRepository invoiceRepo) {
        this.patientRepo     = patientRepo;
        this.dentistRepo     = dentistRepo;
        this.appointmentRepo = appointmentRepo;
        this.treatmentRepo   = treatmentRepo;
        this.invoiceRepo     = invoiceRepo;
    }

    @Cacheable(value = "dashboard", key = "'global'")
    public DashboardStats getStats() {
        return new DashboardStats(
                patientRepo.countByActiveTrue(),
                dentistRepo.countByActiveTrue(),
                appointmentRepo.countByDeletedFalse(),
                treatmentRepo.countByDeletedFalse(),
                invoiceRepo.countByDeletedFalse()
        );
    }
}
