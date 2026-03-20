package com.dentalclinic.invoice.application.mapper;

import com.dentalclinic.domain.valueobject.Money;
import com.dentalclinic.invoice.application.dto.InvoiceRequest;
import com.dentalclinic.invoice.application.dto.InvoiceResponse;
import com.dentalclinic.invoice.domain.model.Invoice;
import com.dentalclinic.invoice.domain.valueobject.InvoiceStatus;
import java.time.LocalDate;
import java.util.UUID;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface InvoiceMapper {

    InvoiceResponse toResponse(Invoice entity);

}
