-- Логическая схема прототипа; Flask-SQLAlchemy создаёт эти таблицы автоматически.
CREATE TABLE users (id SERIAL PRIMARY KEY, full_name VARCHAR(150) NOT NULL, role VARCHAR(30) NOT NULL);
CREATE TABLE storage_cells (id SERIAL PRIMARY KEY, code VARCHAR(30) UNIQUE NOT NULL, zone VARCHAR(30) NOT NULL DEFAULT 'storage', is_active BOOLEAN NOT NULL DEFAULT TRUE);
CREATE TABLE orders (id SERIAL PRIMARY KEY, tracking_number VARCHAR(100) UNIQUE NOT NULL, marketplace VARCHAR(30) NOT NULL, status VARCHAR(30) NOT NULL DEFAULT 'awaiting_issue', cell_id INTEGER REFERENCES storage_cells(id), accepted_by INTEGER REFERENCES users(id), accepted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, note TEXT);
CREATE TABLE operation_log (id SERIAL PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id), user_id INTEGER NOT NULL REFERENCES users(id), operation VARCHAR(40) NOT NULL, created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, details TEXT);
