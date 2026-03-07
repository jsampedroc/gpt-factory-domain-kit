package com.preschoolmanagement.parent.shared.application.mapper;

import com.preschoolmanagement.parent.application.dto.ParentRequest;
import com.preschoolmanagement.parent.application.dto.ParentResponse;
import com.preschoolmanagement.parent.domain.model.Parent;
import org.mapstruct.Mapper;

@Mapper
public interface ParentMapper {

    Parent toDomain(ParentRequest request);

    ParentResponse toResponse(Parent parent);
}