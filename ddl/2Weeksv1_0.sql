-- Database Creation Script

CREATE USER 'twoweeks'@'%' IDENTIFIED BY 'twoweeks';
GRANT USAGE ON *.* TO 'twoweeks'@'%' IDENTIFIED BY 'twoweeks' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;
CREATE DATABASE IF NOT EXISTS twoweeks;
GRANT ALL PRIVILEGES ON twoweeks.* TO 'twoweeks'@'%';


CREATE USER 'twoweeks'@'162.202.206.75' IDENTIFIED BY 'twoweeks';
GRANT USAGE ON *.* TO 'twoweeks'@'162.202.206.75' IDENTIFIED BY 'twoweeks' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;
CREATE DATABASE IF NOT EXISTS twoweeks;
GRANT ALL PRIVILEGES ON twoweeks.* TO 'twoweeks'@'162.202.206.75';


-- Creating Users table
CREATE TABLE `twoweeks`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '',
  `username` VARCHAR(45) NOT NULL COMMENT '',
  `email` VARCHAR(45) NOT NULL COMMENT '',
  `password` VARCHAR(255) NULL COMMENT '',
  `first_name` VARCHAR(45) NULL COMMENT '',
  `last_name` VARCHAR(45) NULL COMMENT '',
  `date_created` DATETIME NOT NULL COMMENT '',
  `last_updated` DATETIME NOT NULL COMMENT '',
  `last_login` DATETIME NULL COMMENT '',
  PRIMARY KEY (`id`, `username`, `email`, `last_updated`, `date_created`)  COMMENT '');



CREATE TABLE `twoweeks`.`bills` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '',
  `user_id` INT NOT NULL COMMENT '',
  `name` VARCHAR(45) NOT NULL COMMENT '',
  `description` VARCHAR(255) NULL COMMENT '',
  `recurring_flag` INT NULL COMMENT '',
  `amount` FLOAT NULL COMMENT '',
  `recurrance` VARCHAR(45) NULL COMMENT '',
  `next_due_date` DATETIME NULL COMMENT '',
  `payment_type_ind` VARCHAR(2) NULL COMMENT '',
  `payment_method` VARCHAR(45) NULL COMMENT '',
  `date_created` DATETIME NOT NULL COMMENT '',
  `last_updated` VARCHAR(45) NOT NULL COMMENT '',
  PRIMARY KEY (`id`)  COMMENT '');
