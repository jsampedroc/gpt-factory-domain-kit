package com.example.application.mapper;

import com.example.application.dto.ExampleRequest;
import com.example.application.dto.ExampleResponse;
import com.example.domain.model.Example;
import org.mapstruct.Mapper;

@Mapper
public interface ExampleMapper {

    Example toDomain(ExampleRequest request);

    ExampleResponse toResponse(Example example);
}