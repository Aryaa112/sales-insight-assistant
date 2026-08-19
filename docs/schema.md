# Northwind Database Schema

This document was generated automatically from the Northwind PostgreSQL database.

## Tables

### categories

**Row count:** 8

| Column | Data Type | Nullable |
|---|---|---|
| category_id | smallint | NO |
| category_name | character varying | NO |
| description | text | YES |
| picture | bytea | YES |

### customer_customer_demo

**Row count:** 0

| Column | Data Type | Nullable |
|---|---|---|
| customer_id | character | NO |
| customer_type_id | character | NO |

### customer_demographics

**Row count:** 0

| Column | Data Type | Nullable |
|---|---|---|
| customer_type_id | character | NO |
| customer_desc | text | YES |

### customers

**Row count:** 91

| Column | Data Type | Nullable |
|---|---|---|
| customer_id | character | NO |
| company_name | character varying | NO |
| contact_name | character varying | YES |
| contact_title | character varying | YES |
| address | character varying | YES |
| city | character varying | YES |
| region | character varying | YES |
| postal_code | character varying | YES |
| country | character varying | YES |
| phone | character varying | YES |
| fax | character varying | YES |

### employee_territories

**Row count:** 49

| Column | Data Type | Nullable |
|---|---|---|
| employee_id | smallint | NO |
| territory_id | character varying | NO |

### employees

**Row count:** 9

| Column | Data Type | Nullable |
|---|---|---|
| employee_id | smallint | NO |
| last_name | character varying | NO |
| first_name | character varying | NO |
| title | character varying | YES |
| title_of_courtesy | character varying | YES |
| birth_date | date | YES |
| hire_date | date | YES |
| address | character varying | YES |
| city | character varying | YES |
| region | character varying | YES |
| postal_code | character varying | YES |
| country | character varying | YES |
| home_phone | character varying | YES |
| extension | character varying | YES |
| photo | bytea | YES |
| notes | text | YES |
| reports_to | smallint | YES |
| photo_path | character varying | YES |

### order_details

**Row count:** 2155

| Column | Data Type | Nullable |
|---|---|---|
| order_id | smallint | NO |
| product_id | smallint | NO |
| unit_price | real | NO |
| quantity | smallint | NO |
| discount | real | NO |

### orders

**Row count:** 830

| Column | Data Type | Nullable |
|---|---|---|
| order_id | smallint | NO |
| customer_id | character | YES |
| employee_id | smallint | YES |
| order_date | date | YES |
| required_date | date | YES |
| shipped_date | date | YES |
| ship_via | smallint | YES |
| freight | real | YES |
| ship_name | character varying | YES |
| ship_address | character varying | YES |
| ship_city | character varying | YES |
| ship_region | character varying | YES |
| ship_postal_code | character varying | YES |
| ship_country | character varying | YES |

### products

**Row count:** 77

| Column | Data Type | Nullable |
|---|---|---|
| product_id | smallint | NO |
| product_name | character varying | NO |
| supplier_id | smallint | YES |
| category_id | smallint | YES |
| quantity_per_unit | character varying | YES |
| unit_price | real | YES |
| units_in_stock | smallint | YES |
| units_on_order | smallint | YES |
| reorder_level | smallint | YES |
| discontinued | integer | NO |

### region

**Row count:** 4

| Column | Data Type | Nullable |
|---|---|---|
| region_id | smallint | NO |
| region_description | character | NO |

### shippers

**Row count:** 6

| Column | Data Type | Nullable |
|---|---|---|
| shipper_id | smallint | NO |
| company_name | character varying | NO |
| phone | character varying | YES |

### suppliers

**Row count:** 29

| Column | Data Type | Nullable |
|---|---|---|
| supplier_id | smallint | NO |
| company_name | character varying | NO |
| contact_name | character varying | YES |
| contact_title | character varying | YES |
| address | character varying | YES |
| city | character varying | YES |
| region | character varying | YES |
| postal_code | character varying | YES |
| country | character varying | YES |
| phone | character varying | YES |
| fax | character varying | YES |
| homepage | text | YES |

### territories

**Row count:** 53

| Column | Data Type | Nullable |
|---|---|---|
| territory_id | character varying | NO |
| territory_description | character | NO |
| region_id | smallint | NO |

### us_states

**Row count:** 51

| Column | Data Type | Nullable |
|---|---|---|
| state_id | smallint | NO |
| state_name | character varying | YES |
| state_abbr | character varying | YES |
| state_region | character varying | YES |

## Foreign Key Relationships

| Table | Column | Referenced Table | Referenced Column |
|---|---|---|---|
| customer_customer_demo | customer_id | customers | customer_id |
| customer_customer_demo | customer_type_id | customer_demographics | customer_type_id |
| employee_territories | employee_id | employees | employee_id |
| employee_territories | territory_id | territories | territory_id |
| employees | reports_to | employees | employee_id |
| order_details | order_id | orders | order_id |
| order_details | product_id | products | product_id |
| orders | customer_id | customers | customer_id |
| orders | employee_id | employees | employee_id |
| orders | ship_via | shippers | shipper_id |
| products | category_id | categories | category_id |
| products | supplier_id | suppliers | supplier_id |
| territories | region_id | region | region_id |

## List of Values (LOV)

### customers

**country:**
Argentina, Austria, Belgium, Brazil, Canada

**city:**
Aachen, Albuquerque, Anchorage, Århus, Barcelona

### employees

**title:**
Inside Sales Coordinator, Sales Manager, Sales Representative, Vice President, Sales

**country:**
UK, USA

### products

**category_id:**
1, 2, 3, 4, 5

**supplier_id:**
1, 2, 3, 4, 5

### categories

**category_name:**
Beverages, Condiments, Confections, Dairy Products, Grains/Cereals

### suppliers

**country:**
Australia, Brazil, Canada, Denmark, Finland

**city:**
Ann Arbor, Annecy, Bend, Berlin, Boston

### shippers

**company_name:**
Alliance Shippers, DHL, Federal Shipping, Speedy Express, United Package

### orders

**ship_country:**
Argentina, Austria, Belgium, Brazil, Canada

**ship_city:**
Aachen, Albuquerque, Anchorage, Århus, Barcelona

### territories

**region_id:**
1, 2, 3, 4
