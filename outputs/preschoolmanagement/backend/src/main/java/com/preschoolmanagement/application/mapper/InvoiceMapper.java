package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.InvoiceRequest;
import com.preschoolmanagement.application.dto.InvoiceResponse;
import com.preschoolmanagement.domain.model.Invoice;
import org.mapstruct.Mapper;

@Mapper
public interface InvoiceMapper {

    Invoice toDomain(InvoiceRequest request);

    InvoiceResponse toResponse(Invoice invoice);
}
