package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.ParentRequest;
import com.preschoolmanagement.application.dto.ParentResponse;
import com.preschoolmanagement.domain.model.Parent;
import org.mapstruct.Mapper;

@Mapper
public interface ParentMapper {

    Parent toDomain(ParentRequest request);

    ParentResponse toResponse(Parent parent);
}
