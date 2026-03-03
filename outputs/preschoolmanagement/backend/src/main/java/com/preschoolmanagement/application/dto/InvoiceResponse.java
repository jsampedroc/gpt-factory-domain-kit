package com.preschoolmanagement.application.dto;

public class InvoiceResponse {

    private final String id;
    private final String invoiceNumber;
    private final String status;
    private final String amount;
    private final String dueDate;
    private final String parentName;
    private final String childName;

    public InvoiceResponse(String id, String invoiceNumber, String status, String amount, String dueDate, String parentName, String childName) {
        this.id = id;
        this.invoiceNumber = invoiceNumber;
        this.status = status;
        this.amount = amount;
        this.dueDate = dueDate;
        this.parentName = parentName;
        this.childName = childName;
    }

    public String getId() { return id; }
    public String getInvoiceNumber() { return invoiceNumber; }
    public String getStatus() { return status; }
    public String getAmount() { return amount; }
    public String getDueDate() { return dueDate; }
    public String getParentName() { return parentName; }
    public String getChildName() { return childName; }
}
