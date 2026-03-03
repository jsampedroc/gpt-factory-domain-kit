package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.TeacherRequest;
import com.preschoolmanagement.application.dto.TeacherResponse;
import com.preschoolmanagement.domain.model.Teacher;
import org.mapstruct.Mapper;

@Mapper
public interface TeacherMapper {

    Teacher toDomain(TeacherRequest request);

    TeacherResponse toResponse(Teacher teacher);
}
