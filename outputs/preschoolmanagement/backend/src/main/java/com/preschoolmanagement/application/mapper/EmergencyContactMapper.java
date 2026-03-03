package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.EmergencyContactRequest;
import com.preschoolmanagement.application.dto.EmergencyContactResponse;
import com.preschoolmanagement.domain.model.EmergencyContact;
import org.mapstruct.Mapper;

@Mapper
public interface EmergencyContactMapper {

    EmergencyContact toDomain(EmergencyContactRequest request);

    EmergencyContactResponse toResponse(EmergencyContact emergencyContact);
}
