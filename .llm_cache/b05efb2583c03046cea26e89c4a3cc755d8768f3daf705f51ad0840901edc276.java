package com.preschoolmanagement.child.application.mapper;

import com.preschoolmanagement.child.application.dto.ImmunizationRequest;
import com.preschoolmanagement.child.application.dto.ImmunizationResponse;
import com.preschoolmanagement.child.domain.model.Immunization;
import org.mapstruct.Mapper;

@Mapper
public interface ImmunizationMapper {

    Immunization toDomain(ImmunizationRequest request);

    ImmunizationResponse toResponse(Immunization immunization);
}