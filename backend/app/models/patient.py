invoices = relationship("Invoice", back_populates="patient")
lab_results = relationship("LabResult", back_populates="patient")
appointments = relationship("Appointment", back_populates="patient")