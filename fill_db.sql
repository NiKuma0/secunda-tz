BEGIN;

-- Insert buildings
INSERT INTO buildings (id, address, longitude, latitude) VALUES
    (1, '123 Main St', -73.935242, 40.730610),
    (2, '456 Park Ave', -73.973794, 40.764225),
    (3, '789 Broadway', -73.989308, 40.748817),
    (4, '321 5th Ave', -73.985428, 40.748459),
    (5, '567 Madison Ave', -73.974036, 40.762905),
    (6, '890 Lexington Ave', -73.968285, 40.762466),
    (7, '432 6th Ave', -73.996702, 40.737143),
    (8, '765 3rd Ave', -73.971635, 40.753729),
    (9, '234 7th Ave', -73.995669, 40.743825),
    (10, '876 2nd Ave', -73.969748, 40.750709),
    (11, '543 8th Ave', -73.992960, 40.754672),
    (12, '901 1st Ave', -73.963894, 40.759832);

-- Insert organizations
INSERT INTO organizations (id, name, phone) VALUES
    (1, 'Tech Solutions Inc', '+1-555-0123'),
    (2, 'Healthcare Plus', '+1-555-0124'),
    (3, 'Education First', '+1-555-0125'),
    (4, 'Green Energy Co', '+1-555-0126'),
    (5, 'Financial Services Group', '+1-555-0127'),
    (6, 'Creative Design Studio', '+1-555-0128'),
    (7, 'Legal Consultancy Firm', '+1-555-0129'),
    (8, 'Research & Development Lab', '+1-555-0130'),
    (9, 'Digital Marketing Agency', '+1-555-0131'),
    (10, 'Construction Solutions', '+1-555-0132');

-- Insert specializations with hierarchical structure
INSERT INTO specializations (id, name, parent_id) VALUES
    -- Tech & Software (1-5)
    (1, 'Software Development', NULL),
    (2, 'Web Development', 1),
    (3, 'Mobile Development', 1),
    (4, 'Cloud Computing', NULL),
    (5, 'DevOps', 4),
    
    -- Healthcare (6-10)
    (6, 'Primary Care', NULL),
    (7, 'Pediatrics', 6),
    (8, 'Adult Medicine', 6),
    (9, 'Specialty Care', NULL),
    (10, 'Surgery', 9),
    
    -- Education (11-15)
    (11, 'K-12 Education', NULL),
    (12, 'Elementary Education', 11),
    (13, 'Secondary Education', 11),
    (14, 'Higher Education', NULL),
    (15, 'Professional Training', 14),
    
    -- Energy & Construction (16-20)
    (16, 'Renewable Energy', NULL),
    (17, 'Solar Energy', 16),
    (18, 'Wind Energy', 16),
    (19, 'Construction Management', NULL),
    (20, 'Infrastructure Development', 19),
    
    -- Business & Finance (21-25)
    (21, 'Financial Planning', NULL),
    (22, 'Investment Management', 21),
    (23, 'Risk Assessment', NULL),
    (24, 'Corporate Finance', 21),
    (25, 'Market Analysis', 23);

-- Connect organizations with buildings (many-to-many)
INSERT INTO organization_buildings (organization_id, building_id) VALUES
    -- Tech Solutions Inc has 2 buildings
    (1, 1), (1, 2),
    -- Healthcare Plus has 2 buildings
    (2, 3), (2, 4),
    -- Education First has 1 building
    (3, 5),
    -- Green Energy Co has 1 building
    (4, 6),
    -- Financial Services Group has 2 buildings
    (5, 7), (5, 8),
    -- Creative Design Studio has 1 building
    (6, 9),
    -- Legal Consultancy Firm has 1 building
    (7, 10),
    -- Research & Development Lab has 1 building
    (8, 11),
    -- Digital Marketing Agency has 1 building
    (9, 12),
    -- Construction Solutions has shared building with Tech Solutions
    (10, 1);

-- Connect organizations with specializations (many-to-many)
INSERT INTO organization_specializations (organization_id, specialization_id) VALUES
    -- Tech Solutions Inc
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
    -- Healthcare Plus
    (2, 6), (2, 7), (2, 8), (2, 9), (2, 10),
    -- Education First
    (3, 11), (3, 12), (3, 13), (3, 14), (3, 15),
    -- Green Energy Co
    (4, 16), (4, 17), (4, 18),
    -- Financial Services Group
    (5, 21), (5, 22), (5, 23), (5, 24), (5, 25),
    -- Creative Design Studio
    (6, 2), (6, 3),  -- They do web and mobile development
    -- Legal Consultancy Firm
    (7, 23), -- They do risk assessment
    -- Research & Development Lab
    (8, 4), (8, 16), (8, 17), -- They work on cloud computing and renewable energy
    -- Digital Marketing Agency
    (9, 2), -- They do web development
    -- Construction Solutions
    (10, 19), (10, 20); -- They do construction management and infrastructure

COMMIT;
