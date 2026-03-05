package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.ImmunizationRequest;
import com.preschoolmanagement.application.dto.ImmunizationResponse;
import com.preschoolmanagement.domain.model.Immunization;
import org.mapstruct.Mapper;

@Mapper
public interface ImmunizationMapper {

    Immunization toDomain(ImmunizationRequest request);

    ImmunizationResponse toResponse(Immunization immunization);
}