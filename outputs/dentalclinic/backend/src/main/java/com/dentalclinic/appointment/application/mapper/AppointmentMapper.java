package com.dentalclinic.appointment.application.mapper;

import com.dentalclinic.appointment.application.dto.AppointmentRequest;
import com.dentalclinic.appointment.application.dto.AppointmentResponse;
import com.dentalclinic.appointment.domain.model.Appointment;
import com.dentalclinic.appointment.domain.valueobject.AppointmentStatus;
import java.time.LocalDateTime;
import java.util.UUID;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface AppointmentMapper {

    AppointmentResponse toResponse(Appointment entity);

}
