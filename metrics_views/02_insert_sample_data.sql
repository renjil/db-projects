USE CATALOG renjiharold_demo;
USE SCHEMA superfund_membership;
-- =============================================================================
-- Super Fund Membership - Sample Data Population
-- =============================================================================
-- This script populates the tables with realistic sample data for demo purposes.
-- Run this after 01_create_tables.sql
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Insert EMPLOYERS
-- -----------------------------------------------------------------------------
INSERT INTO employers VALUES
('EMP001', 'Oceanic Mining Ltd', '12345678901', 'Mining', 'Large', 'WA', 'Monthly', 11.5, '2018-01-15', 'Active', CURRENT_TIMESTAMP()),
('EMP002', 'Sydney Tech Solutions', '23456789012', 'Technology', 'Medium', 'NSW', 'Fortnightly', 11.5, '2019-03-22', 'Active', CURRENT_TIMESTAMP()),
('EMP003', 'Melbourne Healthcare Group', '34567890123', 'Healthcare', 'Large', 'VIC', 'Monthly', 12.0, '2017-06-01', 'Active', CURRENT_TIMESTAMP()),
('EMP004', 'Brisbane Construction Co', '45678901234', 'Construction', 'Medium', 'QLD', 'Weekly', 11.5, '2020-02-10', 'Active', CURRENT_TIMESTAMP()),
('EMP005', 'Adelaide Retail Holdings', '56789012345', 'Retail', 'Small', 'SA', 'Monthly', 11.5, '2021-08-05', 'Active', CURRENT_TIMESTAMP()),
('EMP006', 'Perth Financial Services', '67890123456', 'Finance', 'Medium', 'WA', 'Fortnightly', 13.0, '2019-11-20', 'Active', CURRENT_TIMESTAMP()),
('EMP007', 'Hobart Education Trust', '78901234567', 'Education', 'Small', 'TAS', 'Monthly', 11.5, '2022-01-10', 'Active', CURRENT_TIMESTAMP()),
('EMP008', 'Darwin Hospitality Group', '89012345678', 'Hospitality', 'Small', 'NT', 'Fortnightly', 11.5, '2021-04-15', 'Inactive', CURRENT_TIMESTAMP());

-- -----------------------------------------------------------------------------
-- Insert INVESTMENT_OPTIONS
-- -----------------------------------------------------------------------------
INSERT INTO investment_options VALUES
('INV001', 'High Growth', 'Growth', 'High', 8.50, 0.0085, FALSE, TRUE, CURRENT_TIMESTAMP()),
('INV002', 'Balanced Growth', 'Balanced', 'Medium-High', 7.00, 0.0075, TRUE, TRUE, CURRENT_TIMESTAMP()),
('INV003', 'Conservative Balanced', 'Balanced', 'Medium', 5.50, 0.0065, FALSE, TRUE, CURRENT_TIMESTAMP()),
('INV004', 'Capital Stable', 'Conservative', 'Low-Medium', 4.00, 0.0055, FALSE, TRUE, CURRENT_TIMESTAMP()),
('INV005', 'Cash Plus', 'Cash', 'Low', 2.50, 0.0035, FALSE, TRUE, CURRENT_TIMESTAMP()),
('INV006', 'Sustainable Future', 'Ethical', 'Medium-High', 6.80, 0.0090, FALSE, TRUE, CURRENT_TIMESTAMP()),
('INV007', 'Australian Shares', 'Growth', 'High', 9.00, 0.0080, FALSE, TRUE, CURRENT_TIMESTAMP()),
('INV008', 'International Shares', 'Growth', 'High', 8.80, 0.0095, FALSE, TRUE, CURRENT_TIMESTAMP());

-- -----------------------------------------------------------------------------
-- Insert MEMBERS (100 sample members)
-- -----------------------------------------------------------------------------
INSERT INTO members VALUES
('MBR000001', 'James', 'Wilson', '1985-03-15', 'Male', 'james.wilson@email.com', '0412345678', 'NSW', '2000', 'Accumulation', 'Active', '2018-02-01', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000002', 'Sarah', 'Chen', '1990-07-22', 'Female', 'sarah.chen@email.com', '0423456789', 'VIC', '3000', 'Accumulation', 'Active', '2019-05-15', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000003', 'Michael', 'O''Brien', '1978-11-08', 'Male', 'michael.obrien@email.com', '0434567890', 'WA', '6000', 'Accumulation', 'Active', '2017-08-20', 'EMP001', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000004', 'Emma', 'Thompson', '1992-04-30', 'Female', 'emma.thompson@email.com', '0445678901', 'QLD', '4000', 'Accumulation', 'Active', '2020-01-10', 'EMP004', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000005', 'David', 'Kumar', '1965-09-12', 'Male', 'david.kumar@email.com', '0456789012', 'SA', '5000', 'Pension', 'Active', '2015-03-01', 'EMP005', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000006', 'Lisa', 'Martinez', '1988-01-25', 'Female', 'lisa.martinez@email.com', '0467890123', 'NSW', '2010', 'Accumulation', 'Active', '2019-09-05', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000007', 'Robert', 'Johnson', '1970-06-18', 'Male', 'robert.johnson@email.com', '0478901234', 'VIC', '3001', 'Transition to Retirement', 'Active', '2016-11-15', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000008', 'Jennifer', 'Lee', '1995-12-03', 'Female', 'jennifer.lee@email.com', '0489012345', 'WA', '6001', 'Accumulation', 'Active', '2021-07-01', 'EMP001', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000009', 'William', 'Brown', '1982-08-27', 'Male', 'william.brown@email.com', '0490123456', 'QLD', '4001', 'Accumulation', 'Active', '2018-04-20', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000010', 'Amanda', 'Davis', '1975-02-14', 'Female', 'amanda.davis@email.com', '0401234567', 'TAS', '7000', 'Accumulation', 'Active', '2017-02-28', 'EMP007', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000011', 'Christopher', 'Taylor', '1993-10-08', 'Male', 'chris.taylor@email.com', '0412345679', 'NSW', '2020', 'Accumulation', 'Active', '2020-03-15', 'EMP006', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000012', 'Michelle', 'Anderson', '1987-05-19', 'Female', 'michelle.anderson@email.com', '0423456780', 'VIC', '3002', 'Accumulation', 'Active', '2019-01-08', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000013', 'Daniel', 'White', '1960-03-22', 'Male', 'daniel.white@email.com', '0434567891', 'WA', '6002', 'Pension', 'Active', '2014-06-01', 'EMP001', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000014', 'Jessica', 'Harris', '1991-11-30', 'Female', 'jessica.harris@email.com', '0445678902', 'QLD', '4002', 'Accumulation', 'Active', '2021-02-20', 'EMP004', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000015', 'Matthew', 'Clark', '1984-07-05', 'Male', 'matthew.clark@email.com', '0456789013', 'SA', '5001', 'Accumulation', 'Active', '2018-08-10', 'EMP005', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000016', 'Ashley', 'Lewis', '1996-09-17', 'Female', 'ashley.lewis@email.com', '0467890124', 'NSW', '2030', 'Accumulation', 'Active', '2022-01-05', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000017', 'Andrew', 'Walker', '1972-04-11', 'Male', 'andrew.walker@email.com', '0478901235', 'VIC', '3003', 'Transition to Retirement', 'Active', '2015-12-01', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000018', 'Stephanie', 'Hall', '1989-08-24', 'Female', 'stephanie.hall@email.com', '0489012346', 'WA', '6003', 'Accumulation', 'Active', '2019-06-18', 'EMP006', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000019', 'Joshua', 'Allen', '1983-12-07', 'Male', 'joshua.allen@email.com', '0490123457', 'QLD', '4003', 'Accumulation', 'Active', '2017-10-25', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000020', 'Nicole', 'Young', '1977-01-29', 'Female', 'nicole.young@email.com', '0401234568', 'TAS', '7001', 'Accumulation', 'Inactive', '2016-05-12', 'EMP007', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000021', 'Ryan', 'King', '1994-06-14', 'Male', 'ryan.king@email.com', '0412345680', 'NSW', '2040', 'Accumulation', 'Active', '2021-04-01', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000022', 'Lauren', 'Wright', '1986-02-28', 'Female', 'lauren.wright@email.com', '0423456781', 'VIC', '3004', 'Accumulation', 'Active', '2018-09-12', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000023', 'Kevin', 'Scott', '1963-10-03', 'Male', 'kevin.scott@email.com', '0434567892', 'WA', '6004', 'Pension', 'Active', '2013-07-20', 'EMP001', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000024', 'Rachel', 'Green', '1990-05-16', 'Female', 'rachel.green@email.com', '0445678903', 'QLD', '4004', 'Accumulation', 'Active', '2020-06-08', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000025', 'Brandon', 'Adams', '1981-09-21', 'Male', 'brandon.adams@email.com', '0456789014', 'SA', '5002', 'Accumulation', 'Active', '2017-03-15', 'EMP005', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000026', 'Megan', 'Nelson', '1997-03-08', 'Female', 'megan.nelson@email.com', '0467890125', 'NSW', '2050', 'Accumulation', 'Active', '2022-08-20', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000027', 'Justin', 'Carter', '1974-11-25', 'Male', 'justin.carter@email.com', '0478901236', 'VIC', '3005', 'Accumulation', 'Active', '2016-02-10', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000028', 'Samantha', 'Mitchell', '1988-07-12', 'Female', 'samantha.mitchell@email.com', '0489012347', 'WA', '6005', 'Accumulation', 'Active', '2019-11-05', 'EMP006', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000029', 'Tyler', 'Perez', '1985-01-03', 'Male', 'tyler.perez@email.com', '0490123458', 'QLD', '4005', 'Accumulation', 'Active', '2018-05-28', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000030', 'Brittany', 'Roberts', '1979-04-19', 'Female', 'brittany.roberts@email.com', '0401234569', 'TAS', '7002', 'Accumulation', 'Closed', '2015-08-15', 'EMP007', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000031', 'Nathan', 'Turner', '1992-12-22', 'Male', 'nathan.turner@email.com', '0412345681', 'NSW', '2060', 'Accumulation', 'Active', '2021-01-18', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000032', 'Kayla', 'Phillips', '1987-06-07', 'Female', 'kayla.phillips@email.com', '0423456782', 'VIC', '3006', 'Accumulation', 'Active', '2018-10-22', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000033', 'Eric', 'Campbell', '1966-08-30', 'Male', 'eric.campbell@email.com', '0434567893', 'WA', '6006', 'Transition to Retirement', 'Active', '2014-04-10', 'EMP001', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000034', 'Christina', 'Parker', '1993-02-11', 'Female', 'christina.parker@email.com', '0445678904', 'QLD', '4006', 'Accumulation', 'Active', '2020-09-30', 'EMP004', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000035', 'Jacob', 'Evans', '1980-10-26', 'Male', 'jacob.evans@email.com', '0456789015', 'SA', '5003', 'Accumulation', 'Active', '2017-07-05', 'EMP005', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000036', 'Amber', 'Edwards', '1998-04-02', 'Female', 'amber.edwards@email.com', '0467890126', 'NSW', '2070', 'Accumulation', 'Active', '2023-02-14', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000037', 'Aaron', 'Collins', '1973-07-18', 'Male', 'aaron.collins@email.com', '0478901237', 'VIC', '3007', 'Accumulation', 'Active', '2015-05-20', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000038', 'Heather', 'Stewart', '1989-11-09', 'Female', 'heather.stewart@email.com', '0489012348', 'WA', '6007', 'Accumulation', 'Active', '2020-02-25', 'EMP006', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000039', 'Sean', 'Sanchez', '1984-03-24', 'Male', 'sean.sanchez@email.com', '0490123459', 'QLD', '4007', 'Accumulation', 'Active', '2018-08-15', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000040', 'Danielle', 'Morris', '1976-09-06', 'Female', 'danielle.morris@email.com', '0401234570', 'NT', '0800', 'Accumulation', 'Inactive', '2016-12-01', 'EMP008', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000041', 'Patrick', 'Rogers', '1995-05-28', 'Male', 'patrick.rogers@email.com', '0412345682', 'NSW', '2080', 'Accumulation', 'Active', '2022-05-10', 'EMP002', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000042', 'Courtney', 'Reed', '1986-01-14', 'Female', 'courtney.reed@email.com', '0423456783', 'VIC', '3008', 'Accumulation', 'Active', '2019-03-18', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000043', 'Gregory', 'Cook', '1962-12-09', 'Male', 'gregory.cook@email.com', '0434567894', 'WA', '6008', 'Pension', 'Active', '2012-09-01', 'EMP001', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000044', 'Melissa', 'Morgan', '1991-08-21', 'Female', 'melissa.morgan@email.com', '0445678905', 'QLD', '4008', 'Accumulation', 'Active', '2021-06-15', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000045', 'Derek', 'Bell', '1983-04-05', 'Male', 'derek.bell@email.com', '0456789016', 'SA', '5004', 'Accumulation', 'Active', '2018-01-25', 'EMP005', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000046', 'Tiffany', 'Murphy', '1996-10-17', 'Female', 'tiffany.murphy@email.com', '0467890127', 'NSW', '2090', 'Accumulation', 'Active', '2023-01-08', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000047', 'Travis', 'Bailey', '1971-06-30', 'Male', 'travis.bailey@email.com', '0478901238', 'VIC', '3009', 'Transition to Retirement', 'Active', '2014-10-12', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000048', 'Rebecca', 'Rivera', '1990-02-08', 'Female', 'rebecca.rivera@email.com', '0489012349', 'WA', '6009', 'Accumulation', 'Active', '2020-07-20', 'EMP006', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000049', 'Jeremy', 'Cooper', '1982-11-23', 'Male', 'jeremy.cooper@email.com', '0490123460', 'QLD', '4009', 'Accumulation', 'Active', '2017-12-05', 'EMP004', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000050', 'Kelly', 'Richardson', '1978-05-11', 'Female', 'kelly.richardson@email.com', '0401234571', 'TAS', '7003', 'Accumulation', 'Active', '2016-03-22', 'EMP007', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000051', 'Alexander', 'Cox', '1994-09-04', 'Male', 'alexander.cox@email.com', '0412345683', 'NSW', '2100', 'Accumulation', 'Active', '2021-09-01', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000052', 'Victoria', 'Howard', '1985-03-27', 'Female', 'victoria.howard@email.com', '0423456784', 'VIC', '3010', 'Accumulation', 'Active', '2018-06-14', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000053', 'Marcus', 'Ward', '1967-07-20', 'Male', 'marcus.ward@email.com', '0434567895', 'WA', '6010', 'Transition to Retirement', 'Active', '2015-01-28', 'EMP001', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000054', 'Kimberly', 'Torres', '1992-01-13', 'Female', 'kimberly.torres@email.com', '0445678906', 'QLD', '4010', 'Accumulation', 'Active', '2020-11-09', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000055', 'Scott', 'Peterson', '1979-08-06', 'Male', 'scott.peterson@email.com', '0456789017', 'SA', '5005', 'Accumulation', 'Active', '2017-04-18', 'EMP005', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000056', 'Allison', 'Gray', '1997-12-29', 'Female', 'allison.gray@email.com', '0467890128', 'NSW', '2110', 'Accumulation', 'Active', '2023-06-22', 'EMP002', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000057', 'Keith', 'Ramirez', '1970-04-15', 'Male', 'keith.ramirez@email.com', '0478901239', 'VIC', '3011', 'Accumulation', 'Active', '2014-07-30', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000058', 'Monica', 'James', '1988-10-02', 'Female', 'monica.james@email.com', '0489012350', 'WA', '6011', 'Accumulation', 'Active', '2019-08-25', 'EMP006', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000059', 'Shawn', 'Watson', '1981-06-17', 'Male', 'shawn.watson@email.com', '0490123461', 'QLD', '4011', 'Accumulation', 'Active', '2018-02-10', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000060', 'Angela', 'Brooks', '1975-11-28', 'Female', 'angela.brooks@email.com', '0401234572', 'NT', '0801', 'Accumulation', 'Closed', '2015-09-05', 'EMP008', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000061', 'Chad', 'Kelly', '1993-07-10', 'Male', 'chad.kelly@email.com', '0412345684', 'NSW', '2120', 'Accumulation', 'Active', '2022-03-28', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000062', 'Vanessa', 'Sanders', '1986-02-23', 'Female', 'vanessa.sanders@email.com', '0423456785', 'VIC', '3012', 'Accumulation', 'Active', '2019-05-12', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000063', 'Russell', 'Price', '1964-09-16', 'Male', 'russell.price@email.com', '0434567896', 'WA', '6012', 'Pension', 'Active', '2013-02-18', 'EMP001', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000064', 'Catherine', 'Bennett', '1990-04-28', 'Female', 'catherine.bennett@email.com', '0445678907', 'QLD', '4012', 'Accumulation', 'Active', '2021-08-06', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000065', 'Philip', 'Wood', '1980-12-11', 'Male', 'philip.wood@email.com', '0456789018', 'SA', '5006', 'Accumulation', 'Active', '2017-10-30', 'EMP005', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000066', 'Natalie', 'Barnes', '1998-06-04', 'Female', 'natalie.barnes@email.com', '0467890129', 'NSW', '2130', 'Accumulation', 'Active', '2024-01-15', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000067', 'Craig', 'Ross', '1972-01-19', 'Male', 'craig.ross@email.com', '0478901240', 'VIC', '3013', 'Accumulation', 'Active', '2015-04-08', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000068', 'Shannon', 'Henderson', '1987-09-25', 'Female', 'shannon.henderson@email.com', '0489012351', 'WA', '6013', 'Accumulation', 'Active', '2020-01-14', 'EMP006', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000069', 'Douglas', 'Coleman', '1983-05-08', 'Male', 'douglas.coleman@email.com', '0490123462', 'QLD', '4013', 'Accumulation', 'Active', '2018-06-28', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000070', 'Diana', 'Jenkins', '1976-10-21', 'Female', 'diana.jenkins@email.com', '0401234573', 'TAS', '7004', 'Accumulation', 'Active', '2016-08-15', 'EMP007', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000071', 'Vincent', 'Perry', '1995-02-13', 'Male', 'vincent.perry@email.com', '0412345685', 'NSW', '2140', 'Accumulation', 'Active', '2022-10-05', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000072', 'Erica', 'Powell', '1984-08-06', 'Female', 'erica.powell@email.com', '0423456786', 'VIC', '3014', 'Accumulation', 'Active', '2018-12-18', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000073', 'Harry', 'Long', '1961-04-29', 'Male', 'harry.long@email.com', '0434567897', 'WA', '6014', 'Pension', 'Active', '2011-11-22', 'EMP001', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000074', 'Olivia', 'Patterson', '1991-11-12', 'Female', 'olivia.patterson@email.com', '0445678908', 'QLD', '4014', 'Accumulation', 'Active', '2021-04-26', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000075', 'Tony', 'Hughes', '1978-06-24', 'Male', 'tony.hughes@email.com', '0456789019', 'SA', '5007', 'Accumulation', 'Active', '2016-12-10', 'EMP005', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000076', 'Brooke', 'Flores', '1999-01-07', 'Female', 'brooke.flores@email.com', '0467890130', 'NSW', '2150', 'Accumulation', 'Active', '2024-05-20', 'EMP002', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000077', 'Frank', 'Washington', '1969-10-30', 'Male', 'frank.washington@email.com', '0478901241', 'VIC', '3015', 'Accumulation', 'Active', '2014-01-15', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000078', 'Cynthia', 'Butler', '1989-03-18', 'Female', 'cynthia.butler@email.com', '0489012352', 'WA', '6015', 'Accumulation', 'Active', '2020-05-08', 'EMP006', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000079', 'Randy', 'Simmons', '1982-09-01', 'Male', 'randy.simmons@email.com', '0490123463', 'QLD', '4015', 'Accumulation', 'Active', '2017-08-22', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000080', 'Laura', 'Foster', '1974-05-14', 'Female', 'laura.foster@email.com', '0401234574', 'NT', '0802', 'Accumulation', 'Inactive', '2015-02-28', 'EMP008', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000081', 'Raymond', 'Gonzales', '1994-12-26', 'Male', 'raymond.gonzales@email.com', '0412345686', 'NSW', '2160', 'Accumulation', 'Active', '2023-04-12', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000082', 'Paula', 'Bryant', '1985-06-09', 'Female', 'paula.bryant@email.com', '0423456787', 'VIC', '3016', 'Accumulation', 'Active', '2019-07-25', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000083', 'Carl', 'Alexander', '1968-01-22', 'Male', 'carl.alexander@email.com', '0434567898', 'WA', '6016', 'Transition to Retirement', 'Active', '2016-06-05', 'EMP001', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000084', 'Amy', 'Russell', '1992-07-15', 'Female', 'amy.russell@email.com', '0445678909', 'QLD', '4016', 'Accumulation', 'Active', '2021-12-18', 'EMP004', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000085', 'Henry', 'Griffin', '1977-03-28', 'Male', 'henry.griffin@email.com', '0456789020', 'SA', '5008', 'Accumulation', 'Active', '2016-09-12', 'EMP005', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000086', 'Christine', 'Diaz', '2000-08-20', 'Female', 'christine.diaz@email.com', '0467890131', 'NSW', '2170', 'Accumulation', 'Active', '2024-09-08', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000087', 'Albert', 'Hayes', '1971-05-03', 'Male', 'albert.hayes@email.com', '0478901242', 'VIC', '3017', 'Accumulation', 'Active', '2014-11-20', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000088', 'Martha', 'Myers', '1988-11-16', 'Female', 'martha.myers@email.com', '0489012353', 'WA', '6017', 'Accumulation', 'Active', '2020-08-30', 'EMP006', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000089', 'Joe', 'Ford', '1981-04-08', 'Male', 'joe.ford@email.com', '0490123464', 'QLD', '4017', 'Accumulation', 'Active', '2017-05-15', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000090', 'Teresa', 'Hamilton', '1973-12-01', 'Female', 'teresa.hamilton@email.com', '0401234575', 'TAS', '7005', 'Accumulation', 'Active', '2015-07-08', 'EMP007', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000091', 'Lawrence', 'Graham', '1996-06-23', 'Male', 'lawrence.graham@email.com', '0412345687', 'NSW', '2180', 'Accumulation', 'Active', '2023-08-25', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000092', 'Gloria', 'Sullivan', '1983-02-05', 'Female', 'gloria.sullivan@email.com', '0423456788', 'VIC', '3018', 'Accumulation', 'Active', '2018-03-10', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000093', 'Gerald', 'Wallace', '1965-09-18', 'Male', 'gerald.wallace@email.com', '0434567899', 'WA', '6018', 'Pension', 'Active', '2012-05-28', 'EMP001', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000094', 'Judy', 'West', '1990-04-01', 'Female', 'judy.west@email.com', '0445678910', 'QLD', '4018', 'Accumulation', 'Active', '2022-02-14', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000095', 'Bruce', 'Cole', '1976-10-14', 'Male', 'bruce.cole@email.com', '0456789021', 'SA', '5009', 'Accumulation', 'Active', '2016-04-25', 'EMP005', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000096', 'Katherine', 'Hunt', '2001-03-09', 'Female', 'katherine.hunt@email.com', '0467890132', 'NSW', '2190', 'Accumulation', 'Active', '2025-01-02', 'EMP002', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000097', 'Eugene', 'Stone', '1970-07-22', 'Male', 'eugene.stone@email.com', '0478901243', 'VIC', '3019', 'Accumulation', 'Active', '2013-10-08', 'EMP003', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000098', 'Anne', 'Black', '1987-01-04', 'Female', 'anne.black@email.com', '0489012354', 'WA', '6019', 'Accumulation', 'Active', '2019-12-15', 'EMP006', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000099', 'Roger', 'Dunn', '1980-08-27', 'Male', 'roger.dunn@email.com', '0490123465', 'QLD', '4019', 'Accumulation', 'Active', '2017-02-20', 'EMP004', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('MBR000100', 'Jean', 'Burns', '1972-04-10', 'Female', 'jean.burns@email.com', '0401234576', 'NT', '0803', 'Accumulation', 'Active', '2014-06-18', 'EMP008', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

-- -----------------------------------------------------------------------------
-- Insert MEMBER_INVESTMENTS (allocations for all members)
-- -----------------------------------------------------------------------------
INSERT INTO member_investments 
SELECT 
    CONCAT('ALLOC', LPAD(ROW_NUMBER() OVER (ORDER BY m.member_id, io.option_id), 6, '0')) as allocation_id,
    m.member_id,
    io.option_id,
    CASE 
        WHEN io.is_default = TRUE THEN 
            CASE WHEN m.member_type = 'Pension' THEN 40 ELSE 60 END
        WHEN io.option_category = 'Growth' AND m.member_type != 'Pension' THEN 25
        WHEN io.option_category = 'Conservative' AND m.member_type = 'Pension' THEN 40
        WHEN io.option_category = 'Cash' THEN 15
        ELSE 0
    END as allocation_percent,
    ROUND(
        CASE 
            WHEN m.member_type = 'Pension' THEN 
                (DATEDIFF(CURRENT_DATE(), m.join_date) / 365.0) * 45000 + RAND() * 200000
            WHEN m.member_type = 'Transition to Retirement' THEN 
                (DATEDIFF(CURRENT_DATE(), m.join_date) / 365.0) * 35000 + RAND() * 150000
            ELSE 
                (DATEDIFF(CURRENT_DATE(), m.join_date) / 365.0) * 15000 + RAND() * 50000
        END * 
        (CASE 
            WHEN io.is_default = TRUE THEN 0.6
            WHEN io.option_category = 'Growth' THEN 0.25
            WHEN io.option_category = 'Conservative' THEN 0.10
            WHEN io.option_category = 'Cash' THEN 0.05
            ELSE 0
        END), 2
    ) as current_balance,
    DATE_ADD(m.join_date, CAST(RAND() * 30 AS INT)) as effective_date,
    CURRENT_TIMESTAMP() as created_at,
    CURRENT_TIMESTAMP() as updated_at
FROM members m
CROSS JOIN investment_options io
WHERE 
    (io.is_default = TRUE) 
    OR (io.option_category = 'Growth' AND io.option_id = 'INV001' AND m.member_type != 'Pension')
    OR (io.option_category = 'Conservative' AND io.option_id = 'INV004' AND m.member_type = 'Pension')
    OR (io.option_category = 'Cash' AND io.option_id = 'INV005');

-- -----------------------------------------------------------------------------
-- Insert CONTRIBUTIONS (historical contributions)
-- -----------------------------------------------------------------------------
-- Generate contributions for each member across financial years
INSERT INTO contributions
SELECT 
    CONCAT('CONT', LPAD(ROW_NUMBER() OVER (ORDER BY m.member_id, fy, contrib_month), 8, '0')) as contribution_id,
    m.member_id,
    m.employer_id,
    contribution_types.contribution_type,
    DATE_ADD(
        TO_DATE(CONCAT(fy_start, '-07-01')), 
        contrib_month * 30
    ) as contribution_date,
    CONCAT('FY', fy) as financial_year,
    ROUND(
        CASE 
            WHEN contribution_types.contribution_type = 'Employer SG' THEN 
                (5000 + RAND() * 3000) * 
                CASE 
                    WHEN e.industry = 'Mining' THEN 1.3
                    WHEN e.industry = 'Finance' THEN 1.2
                    WHEN e.industry = 'Technology' THEN 1.15
                    ELSE 1.0
                END
            WHEN contribution_types.contribution_type = 'Salary Sacrifice' THEN 
                1500 + RAND() * 2000
            WHEN contribution_types.contribution_type = 'Personal' THEN 
                500 + RAND() * 1500
            WHEN contribution_types.contribution_type = 'Government Co-contribution' THEN 
                200 + RAND() * 300
            ELSE 
                1000 + RAND() * 2000
        END, 2
    ) as amount,
    CASE 
        WHEN contribution_types.contribution_type IN ('Employer SG', 'Salary Sacrifice') THEN TRUE 
        ELSE FALSE 
    END as is_concessional,
    CASE 
        WHEN contribution_types.contribution_type IN ('Employer SG', 'Salary Sacrifice') THEN 'SuperStream'
        WHEN contribution_types.contribution_type = 'Personal' THEN 'BPAY'
        WHEN contribution_types.contribution_type = 'Rollover In' THEN 'Rollover'
        ELSE 'Direct Debit'
    END as payment_method,
    'Processed' as status,
    CURRENT_TIMESTAMP() as created_at
FROM members m
JOIN employers e ON m.employer_id = e.employer_id
CROSS JOIN (SELECT 2021 as fy, 2020 as fy_start UNION ALL SELECT 2022, 2021 UNION ALL SELECT 2023, 2022 UNION ALL SELECT 2024, 2023 UNION ALL SELECT 2025, 2024) fy_years
CROSS JOIN (SELECT 0 as contrib_month UNION ALL SELECT 3 UNION ALL SELECT 6 UNION ALL SELECT 9) months
CROSS JOIN (
    SELECT 'Employer SG' as contribution_type 
    UNION ALL SELECT 'Salary Sacrifice' 
    UNION ALL SELECT 'Personal'
) contribution_types
WHERE 
    m.membership_status = 'Active'
    AND m.member_type = 'Accumulation'
    AND fy_years.fy >= YEAR(m.join_date) - (CASE WHEN MONTH(m.join_date) >= 7 THEN 0 ELSE 1 END)
    AND (
        contribution_types.contribution_type = 'Employer SG' 
        OR (contribution_types.contribution_type = 'Salary Sacrifice' AND RAND() > 0.6)
        OR (contribution_types.contribution_type = 'Personal' AND RAND() > 0.75)
    );

-- Add some government co-contributions for eligible members
INSERT INTO contributions
SELECT 
    CONCAT('CONT', LPAD(1000000 + ROW_NUMBER() OVER (ORDER BY m.member_id, fy), 8, '0')) as contribution_id,
    m.member_id,
    NULL as employer_id,
    'Government Co-contribution' as contribution_type,
    TO_DATE(CONCAT(fy, '-06-30')) as contribution_date,
    CONCAT('FY', fy) as financial_year,
    ROUND(200 + RAND() * 300, 2) as amount,
    FALSE as is_concessional,
    'Direct Debit' as payment_method,
    'Processed' as status,
    CURRENT_TIMESTAMP() as created_at
FROM members m
CROSS JOIN (SELECT 2022 as fy UNION ALL SELECT 2023 UNION ALL SELECT 2024) fy_years
WHERE 
    m.membership_status = 'Active'
    AND m.member_type = 'Accumulation'
    AND RAND() > 0.85;

-- -----------------------------------------------------------------------------
-- Insert WITHDRAWALS
-- -----------------------------------------------------------------------------
INSERT INTO withdrawals VALUES
('WDR000001', 'MBR000005', 'Pension Payment', '2024-01-15', 'FY2024', 8500.00, 0.00, 8500.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000002', 'MBR000005', 'Pension Payment', '2024-04-15', 'FY2024', 8500.00, 0.00, 8500.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000003', 'MBR000005', 'Pension Payment', '2024-07-15', 'FY2025', 8500.00, 0.00, 8500.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000004', 'MBR000005', 'Pension Payment', '2024-10-15', 'FY2025', 8500.00, 0.00, 8500.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000005', 'MBR000013', 'Pension Payment', '2024-02-01', 'FY2024', 12000.00, 0.00, 12000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000006', 'MBR000013', 'Pension Payment', '2024-05-01', 'FY2024', 12000.00, 0.00, 12000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000007', 'MBR000013', 'Pension Payment', '2024-08-01', 'FY2025', 12000.00, 0.00, 12000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000008', 'MBR000013', 'Pension Payment', '2024-11-01', 'FY2025', 12000.00, 0.00, 12000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000009', 'MBR000023', 'Pension Payment', '2024-03-01', 'FY2024', 15000.00, 0.00, 15000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000010', 'MBR000023', 'Pension Payment', '2024-06-01', 'FY2024', 15000.00, 0.00, 15000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000011', 'MBR000023', 'Pension Payment', '2024-09-01', 'FY2025', 15000.00, 0.00, 15000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000012', 'MBR000023', 'Pension Payment', '2024-12-01', 'FY2025', 15000.00, 0.00, 15000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000013', 'MBR000007', 'Pension Payment', '2024-01-20', 'FY2024', 5000.00, 0.00, 5000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000014', 'MBR000007', 'Pension Payment', '2024-04-20', 'FY2024', 5000.00, 0.00, 5000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000015', 'MBR000007', 'Pension Payment', '2024-07-20', 'FY2025', 5000.00, 0.00, 5000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000016', 'MBR000030', 'Rollover Out', '2023-08-15', 'FY2024', 45000.00, 0.00, 45000.00, 'Other Super Fund', 'Paid', CURRENT_TIMESTAMP()),
('WDR000017', 'MBR000020', 'Rollover Out', '2024-02-28', 'FY2024', 38000.00, 0.00, 38000.00, 'Other Super Fund', 'Paid', CURRENT_TIMESTAMP()),
('WDR000018', 'MBR000060', 'Rollover Out', '2023-11-10', 'FY2024', 52000.00, 0.00, 52000.00, 'Other Super Fund', 'Paid', CURRENT_TIMESTAMP()),
('WDR000019', 'MBR000040', 'Retirement', '2024-06-30', 'FY2024', 125000.00, 18750.00, 106250.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000020', 'MBR000043', 'Pension Payment', '2024-02-15', 'FY2024', 18000.00, 0.00, 18000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000021', 'MBR000043', 'Pension Payment', '2024-05-15', 'FY2024', 18000.00, 0.00, 18000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000022', 'MBR000043', 'Pension Payment', '2024-08-15', 'FY2025', 18000.00, 0.00, 18000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000023', 'MBR000043', 'Pension Payment', '2024-11-15', 'FY2025', 18000.00, 0.00, 18000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000024', 'MBR000063', 'Pension Payment', '2024-03-10', 'FY2024', 20000.00, 0.00, 20000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000025', 'MBR000063', 'Pension Payment', '2024-06-10', 'FY2024', 20000.00, 0.00, 20000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000026', 'MBR000063', 'Pension Payment', '2024-09-10', 'FY2025', 20000.00, 0.00, 20000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000027', 'MBR000063', 'Pension Payment', '2024-12-10', 'FY2025', 20000.00, 0.00, 20000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000028', 'MBR000073', 'Pension Payment', '2024-01-25', 'FY2024', 22000.00, 0.00, 22000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000029', 'MBR000073', 'Pension Payment', '2024-04-25', 'FY2024', 22000.00, 0.00, 22000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000030', 'MBR000073', 'Pension Payment', '2024-07-25', 'FY2025', 22000.00, 0.00, 22000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000031', 'MBR000093', 'Pension Payment', '2024-02-20', 'FY2024', 16000.00, 0.00, 16000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000032', 'MBR000093', 'Pension Payment', '2024-05-20', 'FY2024', 16000.00, 0.00, 16000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000033', 'MBR000093', 'Pension Payment', '2024-08-20', 'FY2025', 16000.00, 0.00, 16000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000034', 'MBR000017', 'Pension Payment', '2024-03-15', 'FY2024', 6000.00, 0.00, 6000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000035', 'MBR000017', 'Pension Payment', '2024-06-15', 'FY2024', 6000.00, 0.00, 6000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000036', 'MBR000017', 'Pension Payment', '2024-09-15', 'FY2025', 6000.00, 0.00, 6000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000037', 'MBR000033', 'Pension Payment', '2024-01-30', 'FY2024', 7500.00, 0.00, 7500.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000038', 'MBR000033', 'Pension Payment', '2024-04-30', 'FY2024', 7500.00, 0.00, 7500.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000039', 'MBR000033', 'Pension Payment', '2024-07-30', 'FY2025', 7500.00, 0.00, 7500.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000040', 'MBR000047', 'Pension Payment', '2024-02-10', 'FY2024', 8000.00, 0.00, 8000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000041', 'MBR000047', 'Pension Payment', '2024-05-10', 'FY2024', 8000.00, 0.00, 8000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000042', 'MBR000047', 'Pension Payment', '2024-08-10', 'FY2025', 8000.00, 0.00, 8000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000043', 'MBR000053', 'Pension Payment', '2024-03-20', 'FY2024', 9000.00, 0.00, 9000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000044', 'MBR000053', 'Pension Payment', '2024-06-20', 'FY2024', 9000.00, 0.00, 9000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000045', 'MBR000053', 'Pension Payment', '2024-09-20', 'FY2025', 9000.00, 0.00, 9000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000046', 'MBR000083', 'Pension Payment', '2024-01-05', 'FY2024', 7000.00, 0.00, 7000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000047', 'MBR000083', 'Pension Payment', '2024-04-05', 'FY2024', 7000.00, 0.00, 7000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP()),
('WDR000048', 'MBR000083', 'Pension Payment', '2024-07-05', 'FY2025', 7000.00, 0.00, 7000.00, 'Bank Account', 'Paid', CURRENT_TIMESTAMP());

-- -----------------------------------------------------------------------------
-- Insert FEES
-- -----------------------------------------------------------------------------
-- Generate quarterly administration fees for all active members
INSERT INTO fees
SELECT 
    CONCAT('FEE', LPAD(ROW_NUMBER() OVER (ORDER BY m.member_id, quarter), 8, '0')) as fee_id,
    m.member_id,
    'Administration' as fee_type,
    DATE_ADD(TO_DATE(CONCAT(year, '-', quarter * 3, '-01')), -1) as fee_date,
    CONCAT('FY', CASE WHEN quarter >= 3 THEN year + 1 ELSE year END) as financial_year,
    ROUND(25 + RAND() * 10, 2) as amount,
    'Quarterly administration fee' as description,
    CURRENT_TIMESTAMP() as created_at
FROM members m
CROSS JOIN (SELECT 2023 as year UNION ALL SELECT 2024) years
CROSS JOIN (SELECT 1 as quarter UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) quarters
WHERE m.membership_status IN ('Active', 'Inactive');

-- Add insurance fees for members with insurance
INSERT INTO fees
SELECT 
    CONCAT('FEE', LPAD(2000000 + ROW_NUMBER() OVER (ORDER BY m.member_id, month), 8, '0')) as fee_id,
    m.member_id,
    'Insurance' as fee_type,
    TO_DATE(CONCAT(year, '-', LPAD(month, 2, '0'), '-28')) as fee_date,
    CONCAT('FY', CASE WHEN month >= 7 THEN year + 1 ELSE year END) as financial_year,
    ROUND(
        CASE 
            WHEN YEAR(m.date_of_birth) < 1970 THEN 45 + RAND() * 30
            WHEN YEAR(m.date_of_birth) < 1985 THEN 25 + RAND() * 20
            ELSE 15 + RAND() * 10
        END, 2
    ) as amount,
    'Monthly insurance premium' as description,
    CURRENT_TIMESTAMP() as created_at
FROM members m
CROSS JOIN (SELECT 2024 as year) years
CROSS JOIN (SELECT 1 as month UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12) months
WHERE m.insurance_opted_in = TRUE AND m.membership_status = 'Active';

-- Add investment management fees (annual)
INSERT INTO fees
SELECT 
    CONCAT('FEE', LPAD(3000000 + ROW_NUMBER() OVER (ORDER BY m.member_id), 8, '0')) as fee_id,
    m.member_id,
    'Investment' as fee_type,
    TO_DATE('2024-06-30') as fee_date,
    'FY2024' as financial_year,
    ROUND(COALESCE(mb.total_balance, 0) * 0.005, 2) as amount,
    'Annual investment management fee' as description,
    CURRENT_TIMESTAMP() as created_at
FROM members m
LEFT JOIN (
    SELECT member_id, SUM(current_balance) as total_balance 
    FROM member_investments 
    GROUP BY member_id
) mb ON m.member_id = mb.member_id
WHERE m.membership_status = 'Active';

