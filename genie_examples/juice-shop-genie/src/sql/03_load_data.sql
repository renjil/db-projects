-- Juice Shop Genie Demo: Load Sample Data
-- This script populates tables with realistic sample data

-- Load Products (15 items across 3 categories)
INSERT INTO ${catalog}.${schema}.products VALUES
(1, 'Green Goddess', 'Juice', 'Medium', 8.99, 120, true, false, 'Kale, Spinach, Apple, Ginger'),
(2, 'Tropical Sunrise', 'Smoothie', 'Large', 10.99, 280, false, false, 'Mango, Pineapple, Coconut, Banana'),
(3, 'Berry Blast', 'Smoothie', 'Medium', 9.49, 220, true, false, 'Blueberry, Strawberry, Raspberry, Almond Milk'),
(4, 'Citrus Burst', 'Juice', 'Small', 6.99, 90, true, false, 'Orange, Grapefruit, Lemon'),
(5, 'Carrot Ginger Zing', 'Juice', 'Medium', 7.99, 110, true, false, 'Carrot, Ginger, Apple, Turmeric'),
(6, 'Protein Power', 'Smoothie', 'Large', 12.99, 380, false, false, 'Banana, Peanut Butter, Oats, Whey Protein'),
(7, 'Immunity Booster', 'Wellness Shot', 'Small', 4.99, 25, true, false, 'Ginger, Turmeric, Lemon, Cayenne'),
(8, 'Beet It', 'Juice', 'Medium', 8.49, 130, true, false, 'Beet, Apple, Carrot, Ginger'),
(9, 'Pumpkin Spice Dream', 'Smoothie', 'Large', 11.49, 310, false, true, 'Pumpkin, Cinnamon, Nutmeg, Oat Milk'),
(10, 'Watermelon Wave', 'Juice', 'Large', 9.99, 150, false, true, 'Watermelon, Mint, Lime'),
(11, 'Detox Green', 'Juice', 'Small', 7.49, 85, true, false, 'Celery, Cucumber, Parsley, Lemon'),
(12, 'Chocolate Banana Bliss', 'Smoothie', 'Medium', 9.99, 320, false, false, 'Banana, Cacao, Almond Butter, Oat Milk'),
(13, 'Apple Pie', 'Smoothie', 'Medium', 9.49, 260, true, true, 'Apple, Cinnamon, Vanilla, Greek Yogurt'),
(14, 'Energy Shot', 'Wellness Shot', 'Small', 5.49, 30, true, false, 'Matcha, Ginger, Lemon, Honey'),
(15, 'Acai Bowl Blend', 'Smoothie', 'Large', 13.99, 420, true, false, 'Acai, Banana, Blueberry, Granola');

-- Load Customers (15 loyalty members across 4 tiers)
INSERT INTO ${catalog}.${schema}.customers VALUES
(1, 'Emma', 'Wilson', 'emma.wilson@email.com', 'Gold', '2023-03-15', 'Downtown'),
(2, 'James', 'Chen', 'james.chen@email.com', 'Platinum', '2022-08-20', 'Westside'),
(3, 'Sofia', 'Rodriguez', 'sofia.r@email.com', 'Silver', '2023-09-01', 'Downtown'),
(4, 'Liam', 'O''Brien', 'liam.ob@email.com', 'Bronze', '2024-01-10', 'Eastside'),
(5, 'Olivia', 'Patel', 'olivia.p@email.com', 'Gold', '2023-05-22', 'Northgate'),
(6, 'Noah', 'Kim', 'noah.kim@email.com', 'Silver', '2023-07-14', 'Downtown'),
(7, 'Ava', 'Johnson', 'ava.j@email.com', 'Platinum', '2022-04-30', 'Westside'),
(8, 'Ethan', 'Williams', 'ethan.w@email.com', 'Bronze', '2024-02-28', 'Eastside'),
(9, 'Isabella', 'Martinez', 'bella.m@email.com', 'Gold', '2023-06-18', 'Northgate'),
(10, 'Mason', 'Brown', 'mason.b@email.com', 'Silver', '2023-11-05', 'Downtown'),
(11, 'Mia', 'Davis', 'mia.davis@email.com', 'Bronze', '2024-03-12', 'Westside'),
(12, 'Lucas', 'Garcia', 'lucas.g@email.com', 'Gold', '2023-02-08', 'Eastside'),
(13, 'Charlotte', 'Lee', 'charlotte.l@email.com', 'Platinum', '2022-11-25', 'Downtown'),
(14, 'Alexander', 'Taylor', 'alex.t@email.com', 'Silver', '2023-10-17', 'Northgate'),
(15, 'Amelia', 'Anderson', 'amelia.a@email.com', 'Bronze', '2024-01-22', 'Westside');

-- Load Orders (40 transactions across March-April 2024)
INSERT INTO ${catalog}.${schema}.orders VALUES
-- March 2024 orders
(1, 1, 1, 2, '2024-03-01', '08:15', 'Downtown', 'Card', 0.00),
(2, 2, 6, 1, '2024-03-01', '09:30', 'Westside', 'Mobile', 1.30),
(3, 3, 3, 1, '2024-03-02', '10:45', 'Downtown', 'Cash', 0.00),
(4, 7, 2, 2, '2024-03-02', '14:20', 'Westside', 'Card', 2.20),
(5, 5, 7, 3, '2024-03-03', '07:00', 'Northgate', 'Mobile', 0.00),
(6, 1, 4, 1, '2024-03-03', '11:30', 'Downtown', 'Card', 0.70),
(7, 13, 15, 1, '2024-03-04', '13:15', 'Downtown', 'Mobile', 1.40),
(8, 6, 8, 2, '2024-03-04', '16:45', 'Downtown', 'Cash', 0.00),
(9, 9, 12, 1, '2024-03-05', '09:00', 'Northgate', 'Card', 1.00),
(10, 4, 5, 1, '2024-03-05', '12:30', 'Eastside', 'Cash', 0.00),
(11, 2, 14, 2, '2024-03-06', '07:30', 'Westside', 'Mobile', 0.55),
(12, 8, 10, 1, '2024-03-06', '15:00', 'Eastside', 'Card', 0.00),
(13, 12, 1, 1, '2024-03-07', '08:45', 'Eastside', 'Card', 0.90),
(14, 3, 9, 1, '2024-03-07', '14:00', 'Downtown', 'Mobile', 0.00),
(15, 10, 3, 2, '2024-03-08', '10:15', 'Downtown', 'Cash', 0.00),
(16, 7, 6, 1, '2024-03-08', '17:30', 'Westside', 'Card', 1.30),
(17, 5, 11, 1, '2024-03-09', '09:30', 'Northgate', 'Mobile', 0.75),
(18, 14, 2, 1, '2024-03-09', '12:00', 'Northgate', 'Card', 0.00),
(19, 1, 7, 2, '2024-03-10', '07:15', 'Downtown', 'Mobile', 0.50),
(20, 11, 4, 1, '2024-03-10', '11:45', 'Westside', 'Cash', 0.00),
-- April 2024 orders
(21, 2, 15, 1, '2024-04-01', '08:00', 'Westside', 'Card', 1.40),
(22, 13, 1, 2, '2024-04-01', '10:30', 'Downtown', 'Mobile', 0.90),
(23, 6, 12, 1, '2024-04-02', '13:15', 'Downtown', 'Card', 1.00),
(24, 9, 5, 2, '2024-04-02', '16:00', 'Northgate', 'Cash', 0.00),
(25, 4, 3, 1, '2024-04-03', '09:45', 'Eastside', 'Mobile', 0.00),
(26, 7, 8, 1, '2024-04-03', '14:30', 'Westside', 'Card', 0.85),
(27, 15, 6, 1, '2024-04-04', '11:00', 'Westside', 'Cash', 0.00),
(28, 1, 2, 2, '2024-04-04', '15:45', 'Downtown', 'Mobile', 2.20),
(29, 3, 14, 1, '2024-04-05', '07:30', 'Downtown', 'Card', 0.00),
(30, 12, 10, 1, '2024-04-05', '12:15', 'Eastside', 'Mobile', 1.00),
(31, 5, 1, 1, '2024-04-06', '08:30', 'Northgate', 'Card', 0.90),
(32, 8, 7, 2, '2024-04-06', '10:00', 'Eastside', 'Cash', 0.00),
(33, 10, 9, 1, '2024-04-07', '13:00', 'Downtown', 'Mobile', 0.00),
(34, 14, 4, 1, '2024-04-07', '16:30', 'Northgate', 'Card', 0.70),
(35, 2, 11, 1, '2024-04-08', '09:15', 'Westside', 'Mobile', 0.75),
(36, 7, 15, 1, '2024-04-08', '14:00', 'Westside', 'Card', 1.40),
(37, 13, 3, 2, '2024-04-09', '11:30', 'Downtown', 'Cash', 0.00),
(38, 1, 6, 1, '2024-04-09', '17:00', 'Downtown', 'Mobile', 1.30),
(39, 9, 2, 1, '2024-04-10', '08:45', 'Northgate', 'Card', 0.00),
(40, 6, 5, 1, '2024-04-10', '12:30', 'Downtown', 'Card', 0.80);
