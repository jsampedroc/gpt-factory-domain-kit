package com.dentalclinic.dentist.infrastructure.persistence.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import java.util.UUID;
import com.dentalclinic.shared.BaseJpaEntity;

@Entity
@Table(name = "dentist")
public class DentistJpaEntity extends BaseJpaEntity {

    @Id
    @GeneratedValue
    private UUID id;

    public UUID getId() { return this.id; }
    public void setId(UUID id) { this.id = id; }

    private String firstName;
    private String lastName;
    private String licenseNumber;
    private UUID dentistId;

    public DentistJpaEntity() {}

    public String getFirstName() { return this.firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }

    public String getLastName() { return this.lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }

    public String getLicenseNumber() { return this.licenseNumber; }
    public void setLicenseNumber(String licenseNumber) { this.licenseNumber = licenseNumber; }

    public UUID getDentistId() { return this.dentistId; }
    public void setDentistId(UUID dentistId) { this.dentistId = dentistId; }

}
