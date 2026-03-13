package com.preschoolmanagement.parent.infrastructure.persistence.entity;

import com.preschoolmanagement.parent.domain.valueobject.Id;
import java.util.List;



@Entity
public class ParentJpaEntity {

    @Id
    @GeneratedValue
    private UUID id;

    public UUID getId() { return this.id; }
    public void setId(UUID id) { this.id = id; }

    private String firstName;
    private String lastName;
    private List<Child> children;

    public ParentJpaEntity() {}

    public String getFirstName() { return this.firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }

    public String getLastName() { return this.lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }

    public List<Child> getChildren() { return this.children; }
    public void setChildren(List<Child> children) { this.children = children; }

}
