package com.preschoolmanagement.child.application.mapper;

import com.preschoolmanagement.child.application.dto.ChildRequest;
import com.preschoolmanagement.child.application.dto.ChildResponse;
import com.preschoolmanagement.child.domain.model.Child;
import org.mapstruct.Mapper;

@Mapper
public interface ChildMapper {

    Child toDomain(ChildRequest request);

    ChildResponse toResponse(Child child);
}