package com.preschoolmanagement.child.shared.application.mapper;

import com.preschoolmanagement.child.shared.application.dto.AllergyRequest;
import com.preschoolmanagement.child.shared.application.dto.AllergyResponse;
import com.preschoolmanagement.child.domain.model.Allergy;
import org.mapstruct.Mapper;

@Mapper
public interface AllergyMapper {

    Allergy toDomain(AllergyRequest request);

    AllergyResponse toResponse(Allergy allergy);
}