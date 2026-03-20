package com.dentalclinic.treatment.domain.model;

import com.dentalclinic.domain.shared.Entity;
import com.dentalclinic.domain.valueobject.Money;
import com.dentalclinic.treatment.domain.valueobject.TreatmentId;
import java.util.UUID;

public class Treatment extends Entity<TreatmentId> {

    private final UUID treatmentId;
    private final UUID appointmentId;
    private final String description;
    private final Money cost;

    public Treatment(TreatmentId id, UUID treatmentId, UUID appointmentId, String description, Money cost) {
        super(id);
        this.treatmentId = treatmentId;
        this.appointmentId = appointmentId;
        this.description = description;
        this.cost = cost;
    }

    public UUID getTreatmentId() { return this.treatmentId; }

    public UUID getAppointmentId() { return this.appointmentId; }

    public String getDescription() { return this.description; }

    public Money getCost() { return this.cost; }

}