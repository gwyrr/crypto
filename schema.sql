-- SCRIPT SQL: Creacion de base de datos y tablas para MySQL
-- Proyecto: Crypto Portfolio API (Programacion V)

CREATE DATABASE IF NOT EXISTS crypto_portfolio;
USE crypto_portfolio;

-- 1. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Tabla Base de Activos (Para herencia polimorfica)
CREATE TABLE IF NOT EXISTS assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Tabla Secundaria de Criptomonedas (Hereda de assets)
CREATE TABLE IF NOT EXISTS cryptos (
    id INT PRIMARY KEY,
    api_id VARCHAR(100),
    FOREIGN KEY (id) REFERENCES assets(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Tabla de Transacciones (Relaciona usuarios y activos)
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    asset_id INT NOT NULL,
    type VARCHAR(10) NOT NULL DEFAULT 'buy',
    amount DOUBLE NOT NULL,
    buy_price DOUBLE NOT NULL,
    date DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
