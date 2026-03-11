package com.preschoolmanagement.child.infrastructure.persistence.entity;

import com.preschoolmanagement.child.domain.valueobject.Id;
import java.time.LocalDate;
import java.util.List;



@Entity
public class ChildJpaEntity {

    @Id
    @GeneratedValue
    private UUID id;

    public UUID getId() { return this.id; }
    public void setId(UUID id) { this.id = id; }

    private String firstName;
    private String lastName;
    private LocalDate birthDate;
    private List<Allergy> allergies;
    private List<Immunization> immunizations;
    private List<AuthorizedPickup> authorizedPickups;

    public ChildJpaEntity() {}

    public String getFirstName() { return this.firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }

    public String getLastName() { return this.lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }

    public LocalDate getBirthDate() { return this.birthDate; }
    public void setBirthDate(LocalDate birthDate) { this.birthDate = birthDate; }

    public List<Allergy> getAllergies() { return this.allergies; }
    public void setAllergies(List<Allergy> allergies) { this.allergies = allergies; }

    public List<Immunization> getImmunizations() { return this.immunizations; }
    public void setImmunizations(List<Immunization> immunizations) { this.immunizations = immunizations; }

    public List<AuthorizedPickup> getAuthorizedPickups() { return this.authorizedPickups; }
    public void setAuthorizedPickups(List<AuthorizedPickup> authorizedPickups) { this.authorizedPickups = authorizedPickups; }

}
