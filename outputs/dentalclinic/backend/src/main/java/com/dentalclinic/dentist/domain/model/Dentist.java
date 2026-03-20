package com.dentalclinic.dentist.domain.model;

import com.dentalclinic.dentist.domain.valueobject.DentistId;
import com.dentalclinic.domain.shared.Entity;
import java.util.UUID;

public class Dentist extends Entity<DentistId> {

    private final String firstName;
    private final String lastName;
    private final String licenseNumber;
    private final UUID dentistId;

    public Dentist(DentistId id, String firstName, String lastName, String licenseNumber, UUID dentistId) {
        super(id);
        this.firstName = firstName;
        this.lastName = lastName;
        this.licenseNumber = licenseNumber;
        this.dentistId = dentistId;
    }

    public String getFirstName() { return this.firstName; }

    public String getLastName() { return this.lastName; }

    public String getLicenseNumber() { return this.licenseNumber; }

    public UUID getDentistId() { return this.dentistId; }

}