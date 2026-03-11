package com.preschoolmanagement.child.application.mapper;

import java.time.LocalDate;
import java.util.List;



@Mapper
public interface ChildMapper {

    Child toDomain(ChildRequest request);

    ChildResponse toResponse(Child child);
}
