-- 1. Criação das Tabelas
CREATE TABLE IF NOT EXISTS departamentos (
    id_dep INT PRIMARY KEY,
    nome_departamento VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT PRIMARY KEY,
    nome_completo VARCHAR(100),
    email VARCHAR(100),
    telefone VARCHAR(20),
    data_nascimento DATE,
    genero VARCHAR(10),
    pais VARCHAR(50),
    cidade VARCHAR(50),
    data_registo DATE,
    segmento_rfm VARCHAR(20),
    aceita_marketing BOOLEAN
);

CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido INT PRIMARY KEY,
    id_cliente INT,
    id_dep INT,
    data_venda TIMESTAMP,
    moeda_original VARCHAR(3),
    valor_bruto DECIMAL(10, 2),
    desconto_aplicado DECIMAL(10, 2),
    custo_frete DECIMAL(10, 2),
    imposto_local DECIMAL(10, 2),
    metodo_pagamento VARCHAR(50),
    status_pagamento VARCHAR(50),
    status_entrega VARCHAR(50),
    transportadora VARCHAR(50),
    plataforma_venda VARCHAR(50),
    utm_source VARCHAR(50),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_dep) REFERENCES departamentos(id_dep)
);

-- 2. Inserção de Dados
INSERT INTO departamentos VALUES 
(1, 'Café Especial'), 
(2, 'Máquinas'), 
(3, 'Acessórios')
ON CONFLICT (id_dep) DO NOTHING;

INSERT INTO clientes VALUES 
(101, 'Ana Silva', 'ana@email.com', '+244900000001', '1985-04-12', 'F', 'Angola', 'Luanda', '2021-01-15', 'VIP', TRUE),
(102, 'Carlos Mendes', 'carlos@email.pt', '+351900000002', '1990-08-22', 'M', 'Portugal', 'Lisboa', '2022-05-10', 'Frequente', FALSE),
(103, 'John Doe', 'john@email.com', '+15550000003', '1978-11-05', 'M', 'EUA', 'Nova Iorque', '2023-02-20', 'Risco', TRUE),
(104, 'Marta Rocha', 'marta@email.br', '+551190000004', '1995-02-18', 'F', 'Brasil', 'São Paulo', '2023-09-01', 'Inativo', FALSE)
ON CONFLICT (id_cliente) DO NOTHING;

INSERT INTO pedidos VALUES 
(1001, 101, 1, '2023-10-15 10:30:00', 'AOA', 125000.00, 5000.00, 2000.00, 14.00, 'Transferência', 'Aprovado', 'Entregue', 'Correios', 'App Mobile', 'instagram'),
(1002, 102, 2, '2023-10-16 14:45:00', 'EUR', 450.00, 0.00, 15.00, 23.00, 'Cartão Crédito', 'Aprovado', 'Em Trânsito', 'DHL', 'Website', 'google'),
(1003, 103, 1, '2023-10-17 09:15:00', 'USD', 85.00, 10.00, 5.00, 8.87, 'PayPal', 'Aprovado', 'Entregue', 'FedEx', 'Website', 'direto'),
(1004, 101, 3, '2023-11-02 16:20:00', 'AOA', 45000.00, 0.00, 1500.00, 14.00, 'Multibanco', 'Pendente', 'Atrasado', 'Correios', 'App Mobile', 'email_marketing')
ON CONFLICT (id_pedido) DO NOTHING;
