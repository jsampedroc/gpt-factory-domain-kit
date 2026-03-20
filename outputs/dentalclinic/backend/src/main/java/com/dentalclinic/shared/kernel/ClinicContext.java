package com.dentalclinic.shared.kernel;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.util.UUID;

@Component
public class ClinicContext {

    @Value("${app.clinic.default-id:00000000-0000-0000-0000-000000000001}")
    private String defaultClinicId;

    public UUID getDefaultClinicId() {
        return UUID.fromString(defaultClinicId);
    }

    // En el futuro, extraerá el clinic_id del JWT
    public UUID current() {
        return getDefaultClinicId();
    }
}
