CREATE TABLE `bills` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Uniquely identifies each transaction for tracking purposes.',
  `user_id` int(11) NOT NULL COMMENT 'Links to bills_payable(id) to track which person the transaction is associated with.',
  `date` date NOT NULL COMMENT 'date of the transaction',
  `amount` int(11) NOT NULL COMMENT 'Stores the amount given or received in the transaction.',
  `given` tinyint(1) NOT NULL COMMENT 'Indicates the transaction type: True (1) if money is given to the person, False (0) if money is received from the person.',
  PRIMARY KEY (`id`),
  KEY `used_id` (`user_id`),
  CONSTRAINT `used_id` FOREIGN KEY (`user_id`) REFERENCES `bills_payable` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci COMMENT='Links to the bills_payable table and stores details of the money borrowed or lent by a person';

INSERT INTO bills VALUES (27, 4, 2025-03-04, 15000, 1);
INSERT INTO bills VALUES (28, 4, 2025-03-04, 5000, 0);
INSERT INTO bills VALUES (29, 5, 2025-03-04, 12000, 1);

CREATE TABLE `bills_payable` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'it helps to uniquely identify the records/individual',
  `name` varchar(50) NOT NULL COMMENT 'Stores the name of the person who owes or has borrowed money from us.',
  `phone_no` varchar(10) NOT NULL COMMENT 'Stores the contact number of the person for communication and to differentiate individuals with the same name.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_bills` (`name`,`phone_no`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci COMMENT='Stores details of individuals or entities to whom the company owes money or from whom it has borrowed funds.';

INSERT INTO bills_payable VALUES (5, 'BALA', '9025640635');
INSERT INTO bills_payable VALUES (6, 'MUPPIDATHI', '123');
INSERT INTO bills_payable VALUES (4, 'MUPPIDATHI', '9500372044');

CREATE TABLE `office_expenses` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'it is used to uniquely track the office expenses record',
  `date` date NOT NULL COMMENT 'stores the date of office expenses',
  `description` varchar(30) NOT NULL COMMENT 'Describes the reason for the office expense and why the amount was spent on the office expenses.',
  `amount` int(11) NOT NULL COMMENT 'Stores the amount spent on office expenses.',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci COMMENT='Stores details of office maintenance expenses, including stationery and other operational costs.';

INSERT INTO office_expenses VALUES (3, 2025-03-04, 'PATHI', 56);
INSERT INTO office_expenses VALUES (4, 2025-03-04, 'PEN', 30);

CREATE TABLE `vehicle` (
  `vehicle_no` varchar(12) NOT NULL COMMENT '''Stores the unique vehicle number used for identification.',
  `image` varchar(50) DEFAULT NULL COMMENT 'Stores the URL of the vehicle image (optional).',
  `model_name` varchar(30) NOT NULL COMMENT 'Stores the brand and model name of the vehicle, such as Yamaha R15.',
  `model_year` int(11) NOT NULL COMMENT 'store the year of vehicle registration(date of birth for vehicle)',
  `cc` int(11) NOT NULL COMMENT 'Stores the engine capacity (CC) of the vehicle.',
  `purchase_date` date NOT NULL COMMENT 'Records the purchase date of the vehicle.',
  `cost_price` int(11) NOT NULL COMMENT 'Records the purchase cost of the vehicle.',
  `fine` int(11) DEFAULT NULL COMMENT 'Records any fines on the vehicle at the time of purchase, which must be added to the total purchase cost.',
  `buyer_name` varchar(50) DEFAULT NULL COMMENT 'Stores the name of the buyer when the vehicle is sold; remains empty until sold.',
  `aadhar_no` varchar(12) DEFAULT NULL COMMENT 'Stores the buyer’s Aadhar number; remains empty until the vehicle is sold.',
  `phone_no` varchar(10) DEFAULT NULL COMMENT 'Stores the buyer’s mobile number; remains empty until the vehicle is sold.',
  `sales_date` date DEFAULT NULL COMMENT 'Records the date when the vehicle was sold.',
  `sales_price` int(11) DEFAULT NULL COMMENT 'Records the total amount agreed upon by the buyer for the vehicle at the time of sale.',
  `received_amount` int(11) DEFAULT NULL COMMENT 'Records the total amount received from the buyer to date, which may be less than the agreed sales price if payment is pending.',
  PRIMARY KEY (`vehicle_no`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci COMMENT='Stores vehicle details related to purchase and sales transactions.';

INSERT INTO vehicle VALUES ('KL31N7871', 'static/vehicle/default_bike.jpg', 'R15', 0, 155, 2025-03-04, 146000, 1000, 'muppidathi', '1234', '9500372044', 2025-03-04, 150000, 149000);
INSERT INTO vehicle VALUES ('TN31N7871', 'static/vehicle/default_bike.jpg', 'TVS', 2016, 100, 2025-03-08, 40000, 0, None, None, None, None, 0, None);

CREATE TABLE `vehicle_expenses` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'it is used to uniquely identify the records.',
  `vehicle_num` varchar(12) NOT NULL COMMENT 'Links to vehicle(vehicle_no) to track all expenses associated with a specific vehicle.',
  `vehicle_expenses_date` date NOT NULL COMMENT 'Records the date when money was spent on vehicle repairs or other expenses.',
  `description` varchar(30) NOT NULL COMMENT 'Describes the reason for the expense and why the amount was spent on the vehicle.',
  `amount` int(11) NOT NULL COMMENT 'Stores the amount(rupees) spent on repairs or other expenses for the vehicle.',
  PRIMARY KEY (`id`),
  KEY `vehicle_no` (`vehicle_num`),
  CONSTRAINT `vehicle_no` FOREIGN KEY (`vehicle_num`) REFERENCES `vehicle` (`vehicle_no`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci COMMENT='Stores details of expenses incurred on vehicle repairs and maintenance before selling it to the customer.';

INSERT INTO vehicle_expenses VALUES (7, 'KL31N7871', 2025-03-04, 'TYRE', 500);

