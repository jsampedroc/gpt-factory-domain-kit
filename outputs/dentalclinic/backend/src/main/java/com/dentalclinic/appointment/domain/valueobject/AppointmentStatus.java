package com.dentalclinic.appointment.domain.valueobject;

import com.dentalclinic.domain.shared.ValueObject;

public class AppointmentStatus {

    private final String value;

    public AppointmentStatus(String value) {
        this.value = value;
    }

    public String getValue() { return this.value; }

}