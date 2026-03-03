package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.ClassroomRequest;
import com.preschoolmanagement.application.dto.ClassroomResponse;
import com.preschoolmanagement.domain.model.Classroom;
import org.mapstruct.Mapper;

@Mapper
public interface ClassroomMapper {

    Classroom toDomain(ClassroomRequest request);

    ClassroomResponse toResponse(Classroom classroom);
}
