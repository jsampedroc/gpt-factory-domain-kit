package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.ChildRequest;
import com.preschoolmanagement.application.dto.ChildResponse;
import com.preschoolmanagement.domain.model.Child;
import org.mapstruct.Mapper;

@Mapper
public interface ChildMapper {

    Child toDomain(ChildRequest request);

    ChildResponse toResponse(Child child);
}