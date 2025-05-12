-- p_aule.sql (DDL aggiornato)
-- Impostazioni iniziali
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------
-- Creazione del database
-- -----------------------------------------------------
DROP DATABASE IF EXISTS `p_aule`;
CREATE DATABASE `p_aule` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `p_aule`;

-- -----------------------------------------------------
-- Tabella `ruoli`
-- -----------------------------------------------------
CREATE TABLE `ruoli` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `nome` ENUM('Amministratore','Docente','Studente') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inserimento ruoli iniziali (facoltativo, se necessario per test)
INSERT INTO `ruoli` (`nome`) VALUES
('Amministratore'),
('Docente'),
('Studente');

-- -----------------------------------------------------
-- Tabella `utente`
-- -----------------------------------------------------
-- Nota: è stata aggiunta la colonna `password` per gestire l'autenticazione
CREATE TABLE `utente` (
  `idUtente` VARCHAR(8) PRIMARY KEY,
  `nome` VARCHAR(30) NOT NULL,
  `cognome` VARCHAR(30) NOT NULL,
  `email` VARCHAR(30) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `ruolo` ENUM('Studente','Docente','Personale') NOT NULL,
  `ruolo_id` INT NOT NULL,
  FOREIGN KEY (`ruolo_id`) REFERENCES `ruoli`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Tabella `aula`
-- -----------------------------------------------------
CREATE TABLE `aula` (
  `idAula` CHAR(4) PRIMARY KEY,
  `disponibilita` TINYINT(1) NOT NULL,
  `tipo` VARCHAR(30) DEFAULT NULL,
  `capienza` INT NOT NULL,
  `ubicazione` VARCHAR(255) NOT NULL,
  `attrezzature` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Tabella `fasce_orarie`
-- -----------------------------------------------------
CREATE TABLE `fasce_orarie` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `codice_ora` VARCHAR(2) NOT NULL,
  `orario_inizio` TIME NOT NULL,
  `orario_fine` TIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inserimento fasce orarie iniziali
INSERT INTO `fasce_orarie` (`codice_ora`, `orario_inizio`, `orario_fine`) VALUES
('01', '08:00:00', '08:50:00'),
('02', '08:50:00', '09:40:00'),
('03', '09:50:00', '10:50:00'),
('04', '10:50:00', '11:45:00'),
('05', '12:00:00', '12:50:00'),
('06', '12:50:00', '13:40:00'),
('07', '13:40:00', '14:30:00');

-- -----------------------------------------------------
-- Tabella `prenotazione`
-- -----------------------------------------------------
CREATE TABLE `prenotazione` (
  `idPreno` INT AUTO_INCREMENT PRIMARY KEY,
  `idAula` CHAR(4) NOT NULL,
  `idUtente` VARCHAR(8) NOT NULL,
  `dataOraInizio` DATETIME NOT NULL,
  `dataOraFine` DATETIME NOT NULL,
  `stato` ENUM('Richiesta','Approvata','Rifiutata') DEFAULT 'Richiesta',
  `motivazione` TEXT,
  FOREIGN KEY (`idAula`) REFERENCES `aula`(`idAula`) ON DELETE CASCADE,
  FOREIGN KEY (`idUtente`) REFERENCES `utente`(`idUtente`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Tabella `allocazioni_aule`
-- -----------------------------------------------------
CREATE TABLE `allocazioni_aule` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `giorno_id` INT NOT NULL,
  `fascia_oraria_id` INT NOT NULL,
  `aula_id` CHAR(4) NOT NULL,
  `classe_id` VARCHAR(10) NOT NULL,
  FOREIGN KEY (`fascia_oraria_id`) REFERENCES `fasce_orarie`(`id`),
  FOREIGN KEY (`aula_id`) REFERENCES `aula`(`idAula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

