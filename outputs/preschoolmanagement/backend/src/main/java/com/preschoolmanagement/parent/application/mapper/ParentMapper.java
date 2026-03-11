package com.preschoolmanagement.parent.application.mapper;

import java.util.List;



@Mapper
public interface ParentMapper {

    Parent toDomain(ParentRequest request);

    ParentResponse toResponse(Parent parent);
}
