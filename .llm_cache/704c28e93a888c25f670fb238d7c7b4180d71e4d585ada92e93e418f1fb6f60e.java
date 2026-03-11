package com.preschoolmanagement.child.application.mapper;

import com.preschoolmanagement.child.application.dto.AllergyRequest;
import com.preschoolmanagement.child.application.dto.AllergyResponse;
import com.preschoolmanagement.child.domain.model.Allergy;
import org.mapstruct.Mapper;

@Mapper
public interface AllergyMapper {

    Allergy toDomain(AllergyRequest request);

    AllergyResponse toResponse(Allergy allergy);
}