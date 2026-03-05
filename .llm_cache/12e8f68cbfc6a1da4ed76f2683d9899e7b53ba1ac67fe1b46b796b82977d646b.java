package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.AllergyRequest;
import com.preschoolmanagement.application.dto.AllergyResponse;
import com.preschoolmanagement.domain.model.Allergy;
import org.mapstruct.Mapper;

@Mapper
public interface AllergyMapper {

    Allergy toDomain(AllergyRequest request);

    AllergyResponse toResponse(Allergy allergy);
}