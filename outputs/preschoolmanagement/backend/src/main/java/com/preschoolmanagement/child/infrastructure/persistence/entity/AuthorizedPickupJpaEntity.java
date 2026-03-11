package com.preschoolmanagement.child.infrastructure.persistence.entity;

import com.preschoolmanagement.child.domain.valueobject.Id;



@Entity
public class AuthorizedPickupJpaEntity {

    @Id
    @GeneratedValue
    private UUID id;

    public UUID getId() { return this.id; }
    public void setId(UUID id) { this.id = id; }

    private String firstName;
    private String lastName;
    private String relationship;
    private String contactNumber;

    public AuthorizedPickupJpaEntity() {}

    public String getFirstName() { return this.firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }

    public String getLastName() { return this.lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }

    public String getRelationship() { return this.relationship; }
    public void setRelationship(String relationship) { this.relationship = relationship; }

    public String getContactNumber() { return this.contactNumber; }
    public void setContactNumber(String contactNumber) { this.contactNumber = contactNumber; }

}
