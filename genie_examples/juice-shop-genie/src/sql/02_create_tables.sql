-- Juice Shop Genie Demo: Create Tables
-- This script creates the tables for the Juice Shop demo

-- Products table: Menu items (juices, smoothies, wellness shots)
CREATE OR REPLACE TABLE ${catalog}.${schema}.products (
  product_id INT COMMENT 'Unique product identifier',
  product_name STRING COMMENT 'Name of the juice or smoothie',
  category STRING COMMENT 'Product category: Juice, Smoothie, or Wellness Shot',
  size STRING COMMENT 'Size: Small (12oz), Medium (16oz), Large (24oz)',
  price DECIMAL(6,2) COMMENT 'Price in USD',
  calories INT COMMENT 'Calorie count',
  is_organic BOOLEAN COMMENT 'Whether product uses organic ingredients',
  is_seasonal BOOLEAN COMMENT 'Whether product is seasonal',
  main_ingredients STRING COMMENT 'Primary ingredients'
) COMMENT 'Products menu for the Juice Shop';

-- Customers table: Loyalty program members
CREATE OR REPLACE TABLE ${catalog}.${schema}.customers (
  customer_id INT COMMENT 'Unique customer identifier',
  first_name STRING COMMENT 'Customer first name',
  last_name STRING COMMENT 'Customer last name',
  email STRING COMMENT 'Customer email address',
  membership_tier STRING COMMENT 'Loyalty tier: Bronze, Silver, Gold, Platinum',
  signup_date DATE COMMENT 'Date customer joined loyalty program',
  preferred_store STRING COMMENT 'Preferred store location'
) COMMENT 'Customer loyalty program members';

-- Orders table: Transaction history
CREATE OR REPLACE TABLE ${catalog}.${schema}.orders (
  order_id INT COMMENT 'Unique order identifier',
  customer_id INT COMMENT 'Foreign key to customers table',
  product_id INT COMMENT 'Foreign key to products table',
  quantity INT COMMENT 'Number of items ordered',
  order_date DATE COMMENT 'Date of the order',
  order_time STRING COMMENT 'Time of the order (HH:MM)',
  store_location STRING COMMENT 'Store where order was placed: Downtown, Westside, Eastside, Northgate',
  payment_method STRING COMMENT 'Payment method: Cash, Card, Mobile',
  discount_applied DECIMAL(5,2) COMMENT 'Discount amount in USD'
) COMMENT 'Order transactions for the Juice Shop';
