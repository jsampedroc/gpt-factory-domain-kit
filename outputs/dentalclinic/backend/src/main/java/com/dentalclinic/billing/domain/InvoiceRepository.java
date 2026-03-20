package com.dentalclinic.billing.domain;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface InvoiceRepository extends JpaRepository<Invoice, UUID> {
    List<Invoice> findByClinicIdAndDeletedFalseOrderByIssueDateDesc(UUID clinicId);
    List<Invoice> findByPatientIdAndDeletedFalse(UUID patientId);
    Optional<Invoice> findByIdAndClinicId(UUID id, UUID clinicId);
    Optional<Invoice> findByInvoiceNumberAndClinicId(String invoiceNumber, UUID clinicId);
    @Query("SELECT COALESCE(SUM(i.total), 0) FROM Invoice i WHERE i.clinicId = :clinicId AND i.issueDate >= :from AND i.issueDate <= :to AND i.deleted = false AND i.status != 'CANCELLED'")
    BigDecimal sumTotalByDateRange(UUID clinicId, LocalDate from, LocalDate to);
    long countByClinicIdAndStatusAndDeletedFalse(UUID clinicId, InvoiceStatus status);
}
