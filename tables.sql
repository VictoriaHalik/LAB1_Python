CREATE TABLE clients(
    client_id INTEGER PRIMARY KEY,
    first_name VARCHAR,
    surname VARCHAR,
    email VARCHAR,
    password VARCHAR,
    age INTEGER
);

CREATE TABLE credits(
    credit_id INTEGER PRIMARY KEY,
    sum_take INTEGER,
    sum_pay INTEGER,
    pay_off BOOLEAN,
    month_sum INTEGER,
    sum_paid INTEGER,
    sum_left INTEGER,
    month_paid INTEGER,
    start_date DATE,
    finish_date DATE,
    percent INTEGER,
    fk_client_id INTEGER,
    FOREIGN KEY(fk_client_id)  REFERENCES clients(client_id) ON DELETE CASCADE
);

CREATE TABLE budget(
    is_empty BOOLEAN PRIMARY KEY,
    available_sum INTEGER
);
