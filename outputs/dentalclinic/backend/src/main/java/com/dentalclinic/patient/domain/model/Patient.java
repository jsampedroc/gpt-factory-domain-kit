package com.dentalclinic.patient.domain.model;

import com.dentalclinic.domain.shared.Entity;
import com.dentalclinic.patient.domain.valueobject.PatientId;
import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class Patient extends Entity<PatientId> {

    private final String fullName;
    private final String firstName;
    private final String lastName;
    private final LocalDate birthDate;
    private final String dniNie;
    private final String email;
    private final String phone;
    private final String gender;
    private final String bloodType;
    private final String address;
    private final String city;
    private final String postalCode;
    private final String notes;
    private final boolean active;
    private final List<String> clinicalAlerts;
    private final UUID clinicId;
    private final Instant createdAt;

    public Patient(PatientId id, String fullName, String firstName, String lastName,
                   LocalDate birthDate, String dniNie, String email, String phone,
                   String gender, String bloodType, String address, String city,
                   String postalCode, String notes, boolean active,
                   List<String> clinicalAlerts, UUID clinicId, Instant createdAt) {
        super(id);
        this.fullName = fullName;
        this.firstName = firstName;
        this.lastName = lastName;
        this.birthDate = birthDate;
        this.dniNie = dniNie;
        this.email = email;
        this.phone = phone;
        this.gender = gender;
        this.bloodType = bloodType;
        this.address = address;
        this.city = city;
        this.postalCode = postalCode;
        this.notes = notes;
        this.active = active;
        this.clinicalAlerts = clinicalAlerts != null ? clinicalAlerts : new ArrayList<>();
        this.clinicId = clinicId;
        this.createdAt = createdAt;
    }

    public String getFullName() { return fullName; }
    public String getFirstName() { return firstName; }
    public String getLastName() { return lastName; }
    public LocalDate getBirthDate() { return birthDate; }
    public String getDniNie() { return dniNie; }
    public String getEmail() { return email; }
    public String getPhone() { return phone; }
    public String getGender() { return gender; }
    public String getBloodType() { return bloodType; }
    public String getAddress() { return address; }
    public String getCity() { return city; }
    public String getPostalCode() { return postalCode; }
    public String getNotes() { return notes; }
    public boolean isActive() { return active; }
    public List<String> getClinicalAlerts() { return clinicalAlerts; }
    public UUID getClinicId() { return clinicId; }
    public Instant getCreatedAt() { return createdAt; }

    // Legacy compat — kept so existing callers that reference getPatientId() still compile
    public UUID getPatientId() { return getId().value(); }
}
