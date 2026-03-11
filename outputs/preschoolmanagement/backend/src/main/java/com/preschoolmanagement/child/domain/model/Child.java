package com.preschoolmanagement.child.domain.model;

import com.preschoolmanagement.child.domain.valueobject.Allergy;
import com.preschoolmanagement.child.domain.valueobject.ChildId;
import com.preschoolmanagement.child.domain.valueobject.Immunization;
import com.preschoolmanagement.domain.shared.Entity;
import java.time.LocalDate;
import java.util.List;

public class Child extends Entity<ChildId> {

    private final String firstName;
    private final String lastName;
    private final LocalDate birthDate;
    private final List<Allergy> allergies;
    private final List<Immunization> immunizations;
    private final List<AuthorizedPickup> authorizedPickups;

    public Child(ChildId id, String firstName, String lastName, LocalDate birthDate, List<Allergy> allergies, List<Immunization> immunizations, List<AuthorizedPickup> authorizedPickups) {
        super(id);
        this.firstName = firstName;
        this.lastName = lastName;
        this.birthDate = birthDate;
        this.allergies = allergies;
        this.immunizations = immunizations;
        this.authorizedPickups = authorizedPickups;
    }

    public String getFirstName() { return this.firstName; }

    public String getLastName() { return this.lastName; }

    public LocalDate getBirthDate() { return this.birthDate; }

    public List<Allergy> getAllergies() { return this.allergies; }

    public List<Immunization> getImmunizations() { return this.immunizations; }

    public List<AuthorizedPickup> getAuthorizedPickups() { return this.authorizedPickups; }

}
