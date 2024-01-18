FROM python:3-alpine

# Set working directory
WORKDIR /cas

# Install needed Python modules
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy service's sources
COPY carbon-aware-service.py .
ADD flavours flavours

# Add service's data
ADD data /cas/data
WORKDIR /cas/data
RUN python3 generate_numbers.py
WORKDIR /cas

# Expose and run service
EXPOSE 50000
CMD python3 carbon-aware-service.py
