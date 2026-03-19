CREATE TABLE addresses (
    id UUID PRIMARY KEY,
    street VARCHAR(255) NOT NULL,
    number VARCHAR(20) NOT NULL,
    city VARCHAR(120) NOT NULL,
    state VARCHAR(120) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE client_addresses (
    client_id UUID NOT NULL,
    address_id UUID NOT NULL,
    PRIMARY KEY (client_id, address_id),
    CONSTRAINT fk_client_addresses_client
        FOREIGN KEY (client_id)
        REFERENCES clients (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_client_addresses_address
        FOREIGN KEY (address_id)
        REFERENCES addresses (id)
        ON DELETE CASCADE
);

CREATE TABLE employee_addresses (
    employee_id UUID NOT NULL,
    address_id UUID NOT NULL,
    PRIMARY KEY (employee_id, address_id),
    CONSTRAINT fk_employee_addresses_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_employee_addresses_address
        FOREIGN KEY (address_id)
        REFERENCES addresses (id)
        ON DELETE CASCADE
);

CREATE INDEX idx_client_addresses_client_id
    ON client_addresses (client_id);

CREATE INDEX idx_client_addresses_address_id
    ON client_addresses (address_id);

CREATE INDEX idx_employee_addresses_employee_id
    ON employee_addresses (employee_id);

CREATE INDEX idx_employee_addresses_address_id
    ON employee_addresses (address_id);
