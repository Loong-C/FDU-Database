-- 真实图书主数据导入脚本
-- 依赖：建议先执行 create_database.sql、create_tables.sql、insert_sample_data.sql
-- 说明：本脚本基于 数据库数据/cleaned_books.csv 自动生成

-- 1) 出版社去重导入
INSERT IGNORE INTO publisher (publisher_name) VALUES ('A. L. Burt Co.');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('AST');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Addison Wesley');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Addison Wesley Longman');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Addison-Wesley');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Alianza Editorial Sa');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('American Guidance Services Inc.');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Artemis-verlag');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Babblebooks');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Bange C. GmbH');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Bantam Books');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Bedford/St. Martin''s');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Bonnier pocket');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Brand: CreateSpace Independent Publishing Platform');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Cengage Gale');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Cengage Learning');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Chartwell-Bratt');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Clarendon Press');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Classic Books Library');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Computer Science Press');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Cooper Square Pub');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Course Technology Ptr (Sd)');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('CreateSpace Independent Publishing Platform');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Createspace Independent Publishing Platform');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Ecco');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Franklin, Beedle & Associates, Incorporated');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Galera Record');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Gallimard');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Goldmann');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('HarperCollins Publishers');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('HarperCollins Publishers Australia');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Holt Rinehart & Winston');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Holt, Rinehart and Winston');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Holt, Rinehart, and Winston');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Independently Published');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Jones & Bartlett Publishers');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Jones and Bartlett Publishers');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Little, Brown Book Group Limited');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('MIT Press');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Macmillan');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('McGraw-Hill College');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('McGraw-Hill Science/Engineering/Math');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Mcgraw-hill Education');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Michael Knapp');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Murach & Associates, Incorporated, Mike');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Murach Books');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Mybook');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Nasionale Boekhandel');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('National Textbook Company');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('New American Library');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Norton');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Norton & Company Limited, W. W.');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('O''Reilly Media, Incorporated');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Oxford University Press');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Oxford University Press India');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('PEARSON INDIA');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('PIATKUS');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Papermac');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Pearson');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Pearson Education');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Pearson Education, Limited');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Pearson Prentice Hall');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Pearson/Prentice Hall');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Penguin Audio');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Penguin Publishing Group');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Pitman');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Platinum Press LLC');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Prentice Hall');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Prentice-Hall');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Princeton University Press');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Quetzal');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('RBA');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Random House Mondadori');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Routledge');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Scholastic Canada, Limited');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Shroff Publishers & Distributors Pvt. Ltd.');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Simon & Schuster');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Simon & Schuster Audio and Blackstone Publishing');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Springer International Publishing AG');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Summit Press');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Take university press');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Taylor & Francis Group');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('The MIT Press');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('VINTAGE');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('W W Norton & Co Inc');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('W W Norton & Co Inc (Np)');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('W.W. Norton');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('W.W. Norton & Co.');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('WCB/McGraw-Hill');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Whitman');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Wiley');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Wiley & Sons, Limited, John');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Willy');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Wydawnictwo Helion');
INSERT IGNORE INTO publisher (publisher_name) VALUES ('Young Readers'' Classics');

-- 2) 作者去重导入
INSERT IGNORE INTO author (author_name) VALUES ('A. Merritt');
INSERT IGNORE INTO author (author_name) VALUES ('Abraham');
INSERT IGNORE INTO author (author_name) VALUES ('Abraham Silberschatz');
INSERT IGNORE INTO author (author_name) VALUES ('Adam Stewart');
INSERT IGNORE INTO author (author_name) VALUES ('Aharon Yadin');
INSERT IGNORE INTO author (author_name) VALUES ('Albert Camus');
INSERT IGNORE INTO author (author_name) VALUES ('Aldous Huxley');
INSERT IGNORE INTO author (author_name) VALUES ('Alex Jaxson');
INSERT IGNORE INTO author (author_name) VALUES ('Ambrose Bierce');
INSERT IGNORE INTO author (author_name) VALUES ('Anna Akhmatova');
INSERT IGNORE INTO author (author_name) VALUES ('Arthur Bernstein');
INSERT IGNORE INTO author (author_name) VALUES ('Arthur Conan Doyle');
INSERT IGNORE INTO author (author_name) VALUES ('Arthur J. Bernstein');
INSERT IGNORE INTO author (author_name) VALUES ('Barbara Fuchs');
INSERT IGNORE INTO author (author_name) VALUES ('Bernard MacGregor Walker Knox');
INSERT IGNORE INTO author (author_name) VALUES ('Bradley N. Miller');
INSERT IGNORE INTO author (author_name) VALUES ('C. J. Date');
INSERT IGNORE INTO author (author_name) VALUES ('C.J. Date');
INSERT IGNORE INTO author (author_name) VALUES ('Carlos Coronel');
INSERT IGNORE INTO author (author_name) VALUES ('Carol Domblewski');
INSERT IGNORE INTO author (author_name) VALUES ('Caroline Levine');
INSERT IGNORE INTO author (author_name) VALUES ('Carolyn Begg');
INSERT IGNORE INTO author (author_name) VALUES ('Carolyn E. Begg');
INSERT IGNORE INTO author (author_name) VALUES ('Celeste Ng');
INSERT IGNORE INTO author (author_name) VALUES ('Charles Bukowski');
INSERT IGNORE INTO author (author_name) VALUES ('Charlotte Brontë');
INSERT IGNORE INTO author (author_name) VALUES ('Chimamanda Ngozi Adichie');
INSERT IGNORE INTO author (author_name) VALUES ('Chinua Achebe');
INSERT IGNORE INTO author (author_name) VALUES ('Chuck Palahniuk');
INSERT IGNORE INTO author (author_name) VALUES ('Colleen Hoover');
INSERT IGNORE INTO author (author_name) VALUES ('Daniel Suarez');
INSERT IGNORE INTO author (author_name) VALUES ('Dante Alighieri');
INSERT IGNORE INTO author (author_name) VALUES ('David Ascher');
INSERT IGNORE INTO author (author_name) VALUES ('David Damrosch');
INSERT IGNORE INTO author (author_name) VALUES ('David Foster Wallace');
INSERT IGNORE INTO author (author_name) VALUES ('David M. Johnson');
INSERT IGNORE INTO author (author_name) VALUES ('David R. O''Hallaron');
INSERT IGNORE INTO author (author_name) VALUES ('Donna Rosenberg');
INSERT IGNORE INTO author (author_name) VALUES ('E. M. Forster');
INSERT IGNORE INTO author (author_name) VALUES ('Edith Wharton');
INSERT IGNORE INTO author (author_name) VALUES ('Eleanor Hodgman Porter');
INSERT IGNORE INTO author (author_name) VALUES ('Elena Armas');
INSERT IGNORE INTO author (author_name) VALUES ('Ernest H. Shepard');
INSERT IGNORE INTO author (author_name) VALUES ('Eva Martin');
INSERT IGNORE INTO author (author_name) VALUES ('Frances Hodgson Burnett');
INSERT IGNORE INTO author (author_name) VALUES ('Frank N. Magill');
INSERT IGNORE INTO author (author_name) VALUES ('Gary Harrison');
INSERT IGNORE INTO author (author_name) VALUES ('Gowrishankar S');
INSERT IGNORE INTO author (author_name) VALUES ('H. G. Wells');
INSERT IGNORE INTO author (author_name) VALUES ('Hannah Grace');
INSERT IGNORE INTO author (author_name) VALUES ('Harold W. Lawson');
INSERT IGNORE INTO author (author_name) VALUES ('Hector Garcia-Molina');
INSERT IGNORE INTO author (author_name) VALUES ('Henry F. Korth');
INSERT IGNORE INTO author (author_name) VALUES ('Ian Bogost');
INSERT IGNORE INTO author (author_name) VALUES ('Isaac Asimov');
INSERT IGNORE INTO author (author_name) VALUES ('Isabel Allende');
INSERT IGNORE INTO author (author_name) VALUES ('J. Stanley Warford');
INSERT IGNORE INTO author (author_name) VALUES ('Jack Cassidy');
INSERT IGNORE INTO author (author_name) VALUES ('Jack London');
INSERT IGNORE INTO author (author_name) VALUES ('James Martin');
INSERT IGNORE INTO author (author_name) VALUES ('Jean Loup Baer');
INSERT IGNORE INTO author (author_name) VALUES ('Jeffrey D. Ullman');
INSERT IGNORE INTO author (author_name) VALUES ('Jeffrey Eugenides');
INSERT IGNORE INTO author (author_name) VALUES ('Jennifer D. Widom');
INSERT IGNORE INTO author (author_name) VALUES ('Jim Weiss');
INSERT IGNORE INTO author (author_name) VALUES ('Joel Murach');
INSERT IGNORE INTO author (author_name) VALUES ('John D. Carpinelli');
INSERT IGNORE INTO author (author_name) VALUES ('John F. Crawford');
INSERT IGNORE INTO author (author_name) VALUES ('John M. Zelle');
INSERT IGNORE INTO author (author_name) VALUES ('John Mill');
INSERT IGNORE INTO author (author_name) VALUES ('Jorge Luis Borges');
INSERT IGNORE INTO author (author_name) VALUES ('Joshua Welsh');
INSERT IGNORE INTO author (author_name) VALUES ('Justin Seitz');
INSERT IGNORE INTO author (author_name) VALUES ('Kenneth Grahame');
INSERT IGNORE INTO author (author_name) VALUES ('Korth, Henry F.');
INSERT IGNORE INTO author (author_name) VALUES ('Kylene Beers');
INSERT IGNORE INTO author (author_name) VALUES ('Lee Giles');
INSERT IGNORE INTO author (author_name) VALUES ('M. C. Howatson');
INSERT IGNORE INTO author (author_name) VALUES ('M. H. MacDougall');
INSERT IGNORE INTO author (author_name) VALUES ('M. Morris Mano');
INSERT IGNORE INTO author (author_name) VALUES ('M. Tamer Ozsu');
INSERT IGNORE INTO author (author_name) VALUES ('M. Tamer Özsu');
INSERT IGNORE INTO author (author_name) VALUES ('Margaret Atwood');
INSERT IGNORE INTO author (author_name) VALUES ('Mark Lutz');
INSERT IGNORE INTO author (author_name) VALUES ('Martin Puchner');
INSERT IGNORE INTO author (author_name) VALUES ('Martin Seymour-Smith');
INSERT IGNORE INTO author (author_name) VALUES ('Maynard Mack');
INSERT IGNORE INTO author (author_name) VALUES ('Michael Hague');
INSERT IGNORE INTO author (author_name) VALUES ('Michael J. Flynn');
INSERT IGNORE INTO author (author_name) VALUES ('Michael Kifer');
INSERT IGNORE INTO author (author_name) VALUES ('Michael Knapp');
INSERT IGNORE INTO author (author_name) VALUES ('Michael Urban');
INSERT IGNORE INTO author (author_name) VALUES ('Musashi Miyamoto');
INSERT IGNORE INTO author (author_name) VALUES ('Naomi Novik');
INSERT IGNORE INTO author (author_name) VALUES ('Nathaniel Hawthorne');
INSERT IGNORE INTO author (author_name) VALUES ('Naveen ,Kumar and Taneja Sheetal');
INSERT IGNORE INTO author (author_name) VALUES ('Neil Croally');
INSERT IGNORE INTO author (author_name) VALUES ('Neil Reed');
INSERT IGNORE INTO author (author_name) VALUES ('Nick Montfort');
INSERT IGNORE INTO author (author_name) VALUES ('Noam Nisan');
INSERT IGNORE INTO author (author_name) VALUES ('Patricia Clark Smith');
INSERT IGNORE INTO author (author_name) VALUES ('Patrick Valduriez');
INSERT IGNORE INTO author (author_name) VALUES ('Paul Beynon-Davies');
INSERT IGNORE INTO author (author_name) VALUES ('Paul Davis');
INSERT IGNORE INTO author (author_name) VALUES ('Paulo Coelho');
INSERT IGNORE INTO author (author_name) VALUES ('Peck, Harry Thurston');
INSERT IGNORE INTO author (author_name) VALUES ('Peter Rob');
INSERT IGNORE INTO author (author_name) VALUES ('Philip M. Lewis');
INSERT IGNORE INTO author (author_name) VALUES ('Porter');
INSERT IGNORE INTO author (author_name) VALUES ('Programming Languages ACADEMY');
INSERT IGNORE INTO author (author_name) VALUES ('Python Programming');
INSERT IGNORE INTO author (author_name) VALUES ('R. Nageswara Rao');
INSERT IGNORE INTO author (author_name) VALUES ('Raina Telgemeier');
INSERT IGNORE INTO author (author_name) VALUES ('Raj Jain');
INSERT IGNORE INTO author (author_name) VALUES ('Ramez Elmasri');
INSERT IGNORE INTO author (author_name) VALUES ('Randal Bryant');
INSERT IGNORE INTO author (author_name) VALUES ('Randal E. Bryant');
INSERT IGNORE INTO author (author_name) VALUES ('Ray Bradbury');
INSERT IGNORE INTO author (author_name) VALUES ('Reema Thareja');
INSERT IGNORE INTO author (author_name) VALUES ('Robert D. San Souci');
INSERT IGNORE INTO author (author_name) VALUES ('Robert Louis Stevenson');
INSERT IGNORE INTO author (author_name) VALUES ('Roger B. Goodman');
INSERT IGNORE INTO author (author_name) VALUES ('Roy Hyde');
INSERT IGNORE INTO author (author_name) VALUES ('Rudolf Lorenzen');
INSERT IGNORE INTO author (author_name) VALUES ('Sally Thorne');
INSERT IGNORE INTO author (author_name) VALUES ('Sapphire');
INSERT IGNORE INTO author (author_name) VALUES ('Sapphire, Lofton, Ramona');
INSERT IGNORE INTO author (author_name) VALUES ('Sarah N. Lawall');
INSERT IGNORE INTO author (author_name) VALUES ('Sarah Stewart');
INSERT IGNORE INTO author (author_name) VALUES ('Shamkant B. Navathe');
INSERT IGNORE INTO author (author_name) VALUES ('Shamkant Navathe');
INSERT IGNORE INTO author (author_name) VALUES ('Shashwat Pathak');
INSERT IGNORE INTO author (author_name) VALUES ('Shimon Schocken');
INSERT IGNORE INTO author (author_name) VALUES ('Silberschatz Silberschatz');
INSERT IGNORE INTO author (author_name) VALUES ('Sir Paul Harvey');
INSERT IGNORE INTO author (author_name) VALUES ('Spyri, Johanna');
INSERT IGNORE INTO author (author_name) VALUES ('Stephen King');
INSERT IGNORE INTO author (author_name) VALUES ('Sudarshan, S.');
INSERT IGNORE INTO author (author_name) VALUES ('Susan Wittig Albert');
INSERT IGNORE INTO author (author_name) VALUES ('Suzanne Conklin Akbari');
INSERT IGNORE INTO author (author_name) VALUES ('Swati Sharma');
INSERT IGNORE INTO author (author_name) VALUES ('Tayari Jones');
INSERT IGNORE INTO author (author_name) VALUES ('Terry Pratchett');
INSERT IGNORE INTO author (author_name) VALUES ('Thomas Connolly');
INSERT IGNORE INTO author (author_name) VALUES ('Thomas M. Connolly');
INSERT IGNORE INTO author (author_name) VALUES ('Tim Arnold');
INSERT IGNORE INTO author (author_name) VALUES ('Veena A');
INSERT IGNORE INTO author (author_name) VALUES ('Vijaya Kumara Sarma');
INSERT IGNORE INTO author (author_name) VALUES ('Vimal Kumar');
INSERT IGNORE INTO author (author_name) VALUES ('Vincent P. Heuring');
INSERT IGNORE INTO author (author_name) VALUES ('Virginia Woolf');
INSERT IGNORE INTO author (author_name) VALUES ('Wayne Luk');
INSERT IGNORE INTO author (author_name) VALUES ('Wesley Chun');
INSERT IGNORE INTO author (author_name) VALUES ('Wiebke Denecke');
INSERT IGNORE INTO author (author_name) VALUES ('Антон Павлович Чехов');
INSERT IGNORE INTO author (author_name) VALUES ('Фёдор Михайлович Достоевский');

-- 3) 商品与图书主数据导入
INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database system concepts', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780072283631', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780072283631'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780072283631' LIMIT 1), '9780072283631', (SELECT publisher_id FROM publisher WHERE publisher_name = 'WCB/McGraw-Hill' LIMIT 1), '1997-01-01', NULL, 'eng', 840
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780072283631'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780072283631' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Abraham Silberschatz' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Fundamentals of database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780321369574', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780321369574'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321369574' LIMIT 1), '9780321369574', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Pearson' LIMIT 1), '1989-01-01', NULL, 'eng', 1030
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780321369574'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321369574' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Ramez Elmasri' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321369574' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Shamkant B. Navathe' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'A first course in database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780131225206', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780131225206'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780131225206' LIMIT 1), '9780131225206', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Pearson Prentice Hall' LIMIT 1), '1997-01-01', NULL, 'eng', 528
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780131225206'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780131225206' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jeffrey D. Ullman' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780131225206' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jennifer D. Widom' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780357673034', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780357673034'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780357673034' LIMIT 1), '9780357673034', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Cengage Learning' LIMIT 1), '2006-01-01', NULL, 'eng', 812
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780357673034'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780357673034' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Peter Rob' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780357673034' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Carlos Coronel' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Principles of distributed database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9783030262532', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9783030262532'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), '9783030262532', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Springer International Publishing AG' LIMIT 1), '1999-01-01', NULL, 'eng,ger', 691
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9783030262532'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'M. Tamer Özsu' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'M. Tamer Ozsu' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Patrick Valduriez' LIMIT 1), 3;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'An introduction to database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780201144710', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780201144710'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780201144710' LIMIT 1), '9780201144710', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Addison Wesley Longman' LIMIT 1), '1975-01-01', NULL, 'eng', 639
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780201144710'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780201144710' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'C. J. Date' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database Systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781403916013', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781403916013'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781403916013' LIMIT 1), '9781403916013', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Macmillan' LIMIT 1), '1996-01-01', NULL, 'eng,und', 420
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781403916013'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781403916013' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Paul Beynon-Davies' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780760049044', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780760049044'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780760049044' LIMIT 1), '9780760049044', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Course Technology Ptr (Sd)' LIMIT 1), '1993-01-01', NULL, 'eng', 796
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780760049044'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780760049044' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Peter Rob' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780131873254', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780131873254'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780131873254' LIMIT 1), '9780131873254', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Pearson Prentice Hall' LIMIT 1), '2001-01-01', NULL, 'eng', 1152
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780131873254'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780131873254' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Hector Garcia-Molina' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780131873254' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jeffrey D. Ullman' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780131873254' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jennifer D. Widom' LIMIT 1), 3;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database system concepts', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780071217620', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780071217620'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780071217620' LIMIT 1), '9780071217620', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Mcgraw-hill Education' LIMIT 1), '1986-01-01', NULL, 'eng', 694
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780071217620'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780071217620' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Henry F. Korth' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780321210258', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780321210258'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321210258' LIMIT 1), '9780321210258', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Addison-Wesley' LIMIT 1), '1996-01-01', NULL, 'eng', 1374
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780321210258'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321210258' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Thomas M. Connolly' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321210258' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Carolyn E. Begg' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database Systems Concepts', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780072958867', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780072958867'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780072958867' LIMIT 1), '9780072958867', (SELECT publisher_id FROM publisher WHERE publisher_name = 'McGraw-Hill Science/Engineering/Math' LIMIT 1), '2005-01-01', NULL, 'eng', 1168
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780072958867'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780072958867' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Abraham Silberschatz' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Fundamentals of database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780136086208', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780136086208'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780136086208' LIMIT 1), '9780136086208', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Addison-Wesley' LIMIT 1), '2011-01-01', NULL, 'eng', 1172
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780136086208'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780136086208' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Ramez Elmasri' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database System Concepts, 3rd', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780071148108', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780071148108'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780071148108' LIMIT 1), '9780071148108', (SELECT publisher_id FROM publisher WHERE publisher_name = 'McGraw-Hill College' LIMIT 1), '1997-01-01', NULL, NULL, 848
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780071148108'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780071148108' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Abraham' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780071148108' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Korth, Henry F.' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780071148108' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Sudarshan, S.' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780071148108' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Silberschatz Silberschatz' LIMIT 1), 4;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Fundamentals of database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780321415066', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780321415066'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321415066' LIMIT 1), '9780321415066', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Pearson Education, Limited' LIMIT 1), '1999-01-01', NULL, 'eng', 1089
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780321415066'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321415066' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Ramez Elmasri' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321415066' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Shamkant Navathe' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780321228383', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780321228383'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321228383' LIMIT 1), '9780321228383', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Addison-Wesley' LIMIT 1), '2004-01-01', NULL, 'eng', 980
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780321228383'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321228383' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Michael Kifer' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321228383' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Arthur J. Bernstein' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321228383' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Philip M. Lewis' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321228383' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Michael Kifer' LIMIT 1), 4;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780321228383' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Arthur Bernstein' LIMIT 1), 5;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'An introduction to database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780201684193', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780201684193'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780201684193' LIMIT 1), '9780201684193', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Addison-Wesley' LIMIT 1), '2000-01-01', NULL, 'eng', 938
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780201684193'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780201684193' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'C. J. Date' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780201684193' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'C.J. Date' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780132943260', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780132943260'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780132943260' LIMIT 1), '9780132943260', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Addison Wesley' LIMIT 1), '2001-01-01', NULL, 'eng', 1338
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780132943260'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780132943260' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Thomas Connolly' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780132943260' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Carolyn Begg' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Principles of database systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780914894131', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780914894131'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780914894131' LIMIT 1), '9780914894131', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Pitman' LIMIT 1), '1980-01-01', NULL, 'eng', 484
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780914894131'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780914894131' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jeffrey D. Ullman' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Computer system architecture', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781405825160', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781405825160'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781405825160' LIMIT 1), '9781405825160', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Pearson Education, Limited' LIMIT 1), '1983-01-01', NULL, 'eng,und', 531
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781405825160'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781405825160' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'M. Morris Mano' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Computer systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780134123837', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780134123837'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780134123837' LIMIT 1), '9780134123837', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Pearson Education' LIMIT 1), '2002-01-01', NULL, 'eng', 1079
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780134123837'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780134123837' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Randal Bryant' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780134123837' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Randal E. Bryant' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780134123837' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'David R. O''Hallaron' LIMIT 1), 3;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Computer systems design and architecture', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780130484406', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780130484406'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780130484406' LIMIT 1), '9780130484406', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Pearson/Prentice Hall' LIMIT 1), '1997-01-01', NULL, 'eng', 608
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780130484406'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780130484406' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Vincent P. Heuring' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Computer system architecture', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780131757387', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780131757387'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780131757387' LIMIT 1), '9780131757387', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Prentice-Hall' LIMIT 1), '1976-01-01', NULL, 'eng', 525
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780131757387'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780131757387' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'M. Morris Mano' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Computer systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780763771447', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780763771447'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780763771447' LIMIT 1), '9780763771447', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Jones & Bartlett Publishers' LIMIT 1), '1998-01-01', NULL, 'eng', 539
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780763771447'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780763771447' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'J. Stanley Warford' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Computer systems architecture', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780716780328', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780716780328'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780716780328' LIMIT 1), '9780716780328', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Computer Science Press' LIMIT 1), '1980-01-01', NULL, 'eng', 626
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780716780328'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780716780328' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jean Loup Baer' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Computer Systems: A Programmer''s Perspective (3rd Edition)', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780134092669', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780134092669'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780134092669' LIMIT 1), '9780134092669', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Pearson' LIMIT 1), '2015-01-01', NULL, 'eng', 1128
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780134092669'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780134092669' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Randal E. Bryant' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780134092669' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'David R. O''Hallaron' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Understanding computer systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9789173723336', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9789173723336'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9789173723336' LIMIT 1), '9789173723336', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Chartwell-Bratt' LIMIT 1), '1979-01-01', NULL, 'eng', 150
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9789173723336'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9789173723336' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Harold W. Lawson' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Elements of Computing Systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780262640688', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780262640688'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262640688' LIMIT 1), '9780262640688', (SELECT publisher_id FROM publisher WHERE publisher_name = 'MIT Press' LIMIT 1), '2008-01-01', NULL, 'eng', 344
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780262640688'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262640688' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Noam Nisan' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262640688' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Shimon Schocken' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The art of computer systems performance analysis', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781118858356', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781118858356'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781118858356' LIMIT 1), '9781118858356', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Wiley' LIMIT 1), '1991-01-01', NULL, 'eng', 768
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781118858356'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781118858356' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Raj Jain' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Computer Systems Organization and Architecture', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780201612530', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780201612530'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780201612530' LIMIT 1), '9780201612530', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Addison Wesley' LIMIT 1), '2000-01-01', NULL, 'eng', 584
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780201612530'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780201612530' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'John D. Carpinelli' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Elements of Computing Systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780262140874', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780262140874'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262140874' LIMIT 1), '9780262140874', (SELECT publisher_id FROM publisher WHERE publisher_name = 'The MIT Press' LIMIT 1), '2005-01-01', NULL, NULL, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780262140874'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262140874' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Noam Nisan' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262140874' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Shimon Schocken' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Racing the Beam', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780262012577', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780262012577'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262012577' LIMIT 1), '9780262012577', (SELECT publisher_id FROM publisher WHERE publisher_name = 'The MIT Press' LIMIT 1), '2009-01-01', NULL, 'eng', 192
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780262012577'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262012577' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Nick Montfort' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262012577' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Ian Bogost' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Design of real time computer systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780132014007', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780132014007'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780132014007' LIMIT 1), '9780132014007', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Prentice-Hall' LIMIT 1), '1967-01-01', NULL, 'eng', 629
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780132014007'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780132014007' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'James Martin' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Computer Systems Architecture', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781482231069', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781482231069'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781482231069' LIMIT 1), '9781482231069', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Taylor & Francis Group' LIMIT 1), '2016-01-01', NULL, 'eng', 445
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781482231069'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781482231069' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Aharon Yadin' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Simulating computer systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780262132299', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780262132299'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262132299' LIMIT 1), '9780262132299', (SELECT publisher_id FROM publisher WHERE publisher_name = 'MIT Press' LIMIT 1), '1987-01-01', NULL, 'eng', 292
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780262132299'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780262132299' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'M. H. MacDougall' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Computer System Design', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781118009918', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781118009918'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781118009918' LIMIT 1), '9781118009918', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Wiley & Sons, Limited, John' LIMIT 1), '2011-01-01', NULL, 'eng', 320
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781118009918'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781118009918' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Michael J. Flynn' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781118009918' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Wayne Luk' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Programming real-time computer systems', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780137305070', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780137305070'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780137305070' LIMIT 1), '9780137305070', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Prentice-Hall' LIMIT 1), '1965-01-01', NULL, 'eng', 386
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780137305070'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780137305070' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'James Martin' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Core Python Programming', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9789390457151', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9789390457151'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9789390457151' LIMIT 1), '9789390457151', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Willy' LIMIT 1), '2016-01-01', NULL, 'hin,eng', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9789390457151'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9789390457151' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'R. Nageswara Rao' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Black Hat Python', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781593275907', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781593275907'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781593275907' LIMIT 1), '9781593275907', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Wydawnictwo Helion' LIMIT 1), '2014-01-01', NULL, 'eng,pol', 192
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781593275907'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781593275907' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Justin Seitz' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781593275907' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Tim Arnold' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Core Python programming', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780132269933', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780132269933'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780132269933' LIMIT 1), '9780132269933', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Pearson Education' LIMIT 1), '2006-01-01', NULL, 'eng', 1077
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780132269933'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780132269933' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Wesley Chun' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python Programming', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9789354973765', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9789354973765'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9789354973765' LIMIT 1), '9789354973765', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Oxford University Press India' LIMIT 1), '2019-01-01', NULL, 'eng', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9789354973765'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9789354973765' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Reema Thareja' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python programming', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781887902991', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781887902991'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781887902991' LIMIT 1), '9781887902991', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Franklin, Beedle & Associates, Incorporated' LIMIT 1), '2003-01-01', NULL, 'eng', 528
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781887902991'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781887902991' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'John M. Zelle' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Learning Python', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9788173667381', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9788173667381'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9788173667381' LIMIT 1), '9788173667381', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Shroff Publishers & Distributors Pvt. Ltd.' LIMIT 1), '1999-01-01', NULL, 'eng,ger', 591
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9788173667381'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9788173667381' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Mark Lutz' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9788173667381' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'David Ascher' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python Programming Crash Course', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9798846955790', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9798846955790'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9798846955790' LIMIT 1), '9798846955790', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Independently Published' LIMIT 1), '2022-01-01', NULL, 'eng', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9798846955790'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798846955790' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Alex Jaxson' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python Programming', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781951339944', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781951339944'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781951339944' LIMIT 1), '9781951339944', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Platinum Press LLC' LIMIT 1), '2019-01-01', NULL, NULL, 180
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781951339944'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781951339944' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Sarah Stewart' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python Programming', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781542988940', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781542988940'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781542988940' LIMIT 1), '9781542988940', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Createspace Independent Publishing Platform' LIMIT 1), '2016-01-01', NULL, 'eng', 98
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781542988940'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781542988940' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Adam Stewart' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781543252217', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781543252217'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781543252217' LIMIT 1), '9781543252217', (SELECT publisher_id FROM publisher WHERE publisher_name = 'CreateSpace Independent Publishing Platform' LIMIT 1), '2017-01-01', NULL, 'eng', 384
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781543252217'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781543252217' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Joshua Welsh' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python Programming', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9789332585348', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9789332585348'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9789332585348' LIMIT 1), '9789332585348', (SELECT publisher_id FROM publisher WHERE publisher_name = 'PEARSON INDIA' LIMIT 1), '2017-01-01', NULL, NULL, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9789332585348'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9789332585348' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Naveen ,Kumar and Taneja Sheetal' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Introduction to Python Programming', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9780815394372', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780815394372'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780815394372' LIMIT 1), '9780815394372', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Taylor & Francis Group' LIMIT 1), '2018-01-01', NULL, 'eng', 444
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780815394372'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780815394372' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Gowrishankar S' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780815394372' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Veena A' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python programming in context', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781284175554', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781284175554'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781284175554' LIMIT 1), '9781284175554', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Jones and Bartlett Publishers' LIMIT 1), '2009-01-01', NULL, 'eng', 498
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781284175554'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781284175554' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Bradley N. Miller' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python Programming', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781032028491', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781032028491'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781032028491' LIMIT 1), '9781032028491', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Taylor & Francis Group' LIMIT 1), '2021-01-01', NULL, 'eng', 316
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781032028491'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781032028491' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Vijaya Kumara Sarma' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781032028491' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Vimal Kumar' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781032028491' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Swati Sharma' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781032028491' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Shashwat Pathak' LIMIT 1), 4;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Murach''s Python Programming (2nd Edition)', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781943872749', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781943872749'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781943872749' LIMIT 1), '9781943872749', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Murach & Associates, Incorporated, Mike' LIMIT 1), '2016-01-01', NULL, 'eng', 564
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781943872749'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781943872749' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Joel Murach' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781943872749' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Michael Urban' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python for Beginners : 2 Books in 1', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9798722827302', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9798722827302'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9798722827302' LIMIT 1), '9798722827302', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Independently Published' LIMIT 1), '2021-01-01', NULL, 'eng', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9798722827302'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798722827302' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Programming Languages ACADEMY' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Programming Python', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9789350232873', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9789350232873'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9789350232873' LIMIT 1), '9789350232873', (SELECT publisher_id FROM publisher WHERE publisher_name = 'O''Reilly Media, Incorporated' LIMIT 1), '1996-01-01', NULL, 'eng', 1584
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9789350232873'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9789350232873' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Mark Lutz' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Python Programming For Beginners', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781521432341', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781521432341'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781521432341' LIMIT 1), '9781521432341', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Michael Knapp' LIMIT 1), '2015-01-01', NULL, 'eng', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781521432341'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781521432341' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Python Programming' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781521432341' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Michael Knapp' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Murach''s Python Programming', (SELECT category_id FROM category WHERE category_name = '计算机' LIMIT 1), '本', 79.00, 51.35, '9781890774974', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781890774974'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781890774974' LIMIT 1), '9781890774974', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Murach Books' LIMIT 1), '2016-01-01', NULL, 'eng', 590
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781890774974'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781890774974' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Michael Urban' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781890774974' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Joel Murach' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Norton book of classical literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780393034264', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780393034264'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393034264' LIMIT 1), '9780393034264', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Norton' LIMIT 1), '1993-01-01', NULL, 'eng', 866
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780393034264'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393034264' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Bernard MacGregor Walker Knox' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Book of Five Rings', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781548127596', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781548127596'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781548127596' LIMIT 1), '9781548127596', (SELECT publisher_id FROM publisher WHERE publisher_name = 'CreateSpace Independent Publishing Platform' LIMIT 1), '2013-01-01', NULL, 'eng,spa', 50
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781548127596'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781548127596' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Musashi Miyamoto' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Idiot', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781539004950', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781539004950'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781539004950' LIMIT 1), '9781539004950', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Summit Press' LIMIT 1), '1869-01-01', NULL, 'ger,eng,rus', 545
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781539004950'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781539004950' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Фёдор Михайлович Достоевский' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781539004950' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Eva Martin' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Secret Garden', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781977930231', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781977930231'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781977930231' LIMIT 1), '9781977930231', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Brand: CreateSpace Independent Publishing Platform' LIMIT 1), '1911-01-01', NULL, 'eng,spa,und', 256
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781977930231'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781977930231' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Frances Hodgson Burnett' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Treasure Island', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781497354975', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781497354975'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781497354975' LIMIT 1), '9781497354975', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Gallimard' LIMIT 1), '1880-01-01', NULL, 'cor,ger,heb', 248
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781497354975'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781497354975' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Robert Louis Stevenson' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Orlando', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9798681983439', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9798681983439'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9798681983439' LIMIT 1), '9798681983439', (SELECT publisher_id FROM publisher WHERE publisher_name = 'New American Library' LIMIT 1), '1928-01-01', NULL, 'ger,heb,slv', 226
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9798681983439'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798681983439' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Virginia Woolf' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'White Fang', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781847498014', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781847498014'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781847498014' LIMIT 1), '9781847498014', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Young Readers'' Classics' LIMIT 1), '1905-01-01', NULL, 'ger,eng,kor', 237
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781847498014'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781847498014' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jack London' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Moon Pool', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9798461321680', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9798461321680'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9798461321680' LIMIT 1), '9798461321680', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Nasionale Boekhandel' LIMIT 1), '1919-01-01', NULL, 'fre,eng', 286
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9798461321680'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798461321680' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'A. Merritt' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Ethan Frome', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781507585559', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781507585559'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781507585559' LIMIT 1), '9781507585559', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Classic Books Library' LIMIT 1), '1910-01-01', NULL, 'ger,eng,kor', 98
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781507585559'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781507585559' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Edith Wharton' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Scarlet Letter', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9798463083326', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9798463083326'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9798463083326' LIMIT 1), '9798463083326', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Artemis-verlag' LIMIT 1), '1800-01-01', NULL, 'ger,heb,pol', 272
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9798463083326'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798463083326' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Nathaniel Hawthorne' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Heidi', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9782070586646', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9782070586646'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9782070586646' LIMIT 1), '9782070586646', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Whitman' LIMIT 1), '1885-01-01', NULL, 'ger,eng,kor', 284
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9782070586646'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9782070586646' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Spyri, Johanna' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Oxford companion to classical literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780198600817', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780198600817'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780198600817' LIMIT 1), '9780198600817', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Oxford University Press' LIMIT 1), '1989-01-01', NULL, 'eng', 615
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780198600817'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780198600817' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'M. C. Howatson' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Pollyanna', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781070647005', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781070647005'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781070647005' LIMIT 1), '9781070647005', (SELECT publisher_id FROM publisher WHERE publisher_name = 'A. L. Burt Co.' LIMIT 1), '1912-01-01', NULL, 'heb,chi,eng', 194
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781070647005'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781070647005' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Eleanor Hodgman Porter' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781070647005' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Porter' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781070647005' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Neil Reed' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781070647005' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Lee Giles' LIMIT 1), 4;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Harper''s dictionary of classical literature and antiquities', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780815401766', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780815401766'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780815401766' LIMIT 1), '9780815401766', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Cooper Square Pub' LIMIT 1), '1896-01-01', NULL, 'eng', 1701
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780815401766'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780815401766' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Peck, Harry Thurston' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Utilitarianism', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781512151275', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781512151275'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781512151275' LIMIT 1), '9781512151275', (SELECT publisher_id FROM publisher WHERE publisher_name = 'CreateSpace Independent Publishing Platform' LIMIT 1), '1863-01-01', NULL, 'eng', 70
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781512151275'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781512151275' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'John Mill' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Oxford companion to classical literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780198661030', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780198661030'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780198661030' LIMIT 1), '9780198661030', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Clarendon Press' LIMIT 1), '1937-01-01', NULL, 'eng', 468
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780198661030'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780198661030' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Sir Paul Harvey' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Professor', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781975717766', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781975717766'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781975717766' LIMIT 1), '9781975717766', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Mybook' LIMIT 1), '1857-01-01', NULL, 'eng', 244
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781975717766'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781975717766' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Charlotte Brontë' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Classical Literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781136736599', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781136736599'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781136736599' LIMIT 1), '9781136736599', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Routledge' LIMIT 1), '2011-01-01', NULL, 'eng', 432
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781136736599'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781136736599' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Neil Croally' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781136736599' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Roy Hyde' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The reluctant dragon', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9798442512304', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9798442512304'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9798442512304' LIMIT 1), '9798442512304', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Holt, Rinehart, and Winston' LIMIT 1), '1938-01-01', NULL, 'eng', 38
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9798442512304'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798442512304' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Kenneth Grahame' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798442512304' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jim Weiss' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798442512304' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Ernest H. Shepard' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798442512304' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Michael Hague' LIMIT 1), 4;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Norton Anthology of World Literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780393656022', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780393656022'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393656022' LIMIT 1), '9780393656022', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Norton & Company Limited, W. W.' LIMIT 1), '2012-01-01', NULL, 'eng', 1376
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780393656022'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393656022' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Martin Puchner' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393656022' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Suzanne Conklin Akbari' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393656022' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Wiebke Denecke' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393656022' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Barbara Fuchs' LIMIT 1), 4;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393656022' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Caroline Levine' LIMIT 1), 5;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Norton anthology of world literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780393152494', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780393152494'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393152494' LIMIT 1), '9780393152494', (SELECT publisher_id FROM publisher WHERE publisher_name = 'W.W. Norton' LIMIT 1), '2001-01-01', NULL, 'eng', 1896
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780393152494'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393152494' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Sarah N. Lawall' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393152494' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Maynard Mack' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Norton anthology of world literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780393913347', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780393913347'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393913347' LIMIT 1), '9780393913347', (SELECT publisher_id FROM publisher WHERE publisher_name = 'W.W. Norton & Co.' LIMIT 1), '2012-01-01', NULL, 'eng', 1504
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780393913347'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393913347' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Martin Puchner' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Bedford anthology of world literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780312402624', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780312402624'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780312402624' LIMIT 1), '9780312402624', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Bedford/St. Martin''s' LIMIT 1), '2002-01-01', NULL, 'eng', 1150
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780312402624'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780312402624' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Paul Davis' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780312402624' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Gary Harrison' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780312402624' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'David M. Johnson' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780312402624' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Patricia Clark Smith' LIMIT 1), 4;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780312402624' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'John F. Crawford' LIMIT 1), 5;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'World literature -- revised edition', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780030514098', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780030514098'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030514098' LIMIT 1), '9780030514098', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Holt, Rinehart and Winston' LIMIT 1), '1998-01-01', NULL, 'eng', 1504
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780030514098'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030514098' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Susan Wittig Albert' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030514098' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Chinua Achebe' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030514098' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jorge Luis Borges' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030514098' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Albert Camus' LIMIT 1), 4;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030514098' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Антон Павлович Чехов' LIMIT 1), 5;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT '75 Short Masterpieces', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9789994911233', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9789994911233'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9789994911233' LIMIT 1), '9789994911233', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Bantam Books' LIMIT 1), '1961-01-01', NULL, 'eng', 283
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9789994911233'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9789994911233' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Roger B. Goodman' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9789994911233' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Ambrose Bierce' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9789994911233' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Ray Bradbury' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9789994911233' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Антон Павлович Чехов' LIMIT 1), 4;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Brave New World', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781521308578', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781521308578'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781521308578' LIMIT 1), '9781521308578', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Bange C. GmbH' LIMIT 1), '1932-01-01', NULL, 'glg,jpn,cze', 241
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781521308578'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781521308578' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Aldous Huxley' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'World Literature 1999', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780785418283', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780785418283'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780785418283' LIMIT 1), '9780785418283', (SELECT publisher_id FROM publisher WHERE publisher_name = 'American Guidance Services Inc.' LIMIT 1), '1999-01-01', NULL, 'eng', 464
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780785418283'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780785418283' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jack Cassidy' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780785418283' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Arthur Conan Doyle' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780785418283' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Isaac Asimov' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780785418283' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Rudolf Lorenzen' LIMIT 1), 4;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780785418283' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Robert D. San Souci' LIMIT 1), 5;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'What is world literature?', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780691049854', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780691049854'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780691049854' LIMIT 1), '9780691049854', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Princeton University Press' LIMIT 1), '2003-01-01', NULL, 'eng', 324
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780691049854'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780691049854' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'David Damrosch' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The War of the Worlds', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9783257201710', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9783257201710'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9783257201710' LIMIT 1), '9783257201710', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Little, Brown Book Group Limited' LIMIT 1), NULL, NULL, 'ger,eng,mon', 206
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9783257201710'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9783257201710' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'H. G. Wells' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Norton anthology of world literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780393977592', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780393977592'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393977592' LIMIT 1), '9780393977592', (SELECT publisher_id FROM publisher WHERE publisher_name = 'W W Norton & Co Inc' LIMIT 1), '2001-01-01', NULL, 'eng', 563
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780393977592'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393977592' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Sarah N. Lawall' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393977592' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Maynard Mack' LIMIT 1), 2;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'World Literature Instructor''s Manual', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780844254814', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780844254814'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780844254814' LIMIT 1), '9780844254814', (SELECT publisher_id FROM publisher WHERE publisher_name = 'National Textbook Company' LIMIT 1), '1992-01-01', NULL, 'eng', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780844254814'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780844254814' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Donna Rosenberg' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Norton Anthology of World Literature, Vol. F', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780393924510', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780393924510'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393924510' LIMIT 1), '9780393924510', (SELECT publisher_id FROM publisher WHERE publisher_name = 'W W Norton & Co Inc (Np)' LIMIT 1), '2002-01-01', NULL, 'eng', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780393924510'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780393924510' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Sarah N. Lawall' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'World Literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780844254821', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780844254821'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780844254821' LIMIT 1), '9780844254821', (SELECT publisher_id FROM publisher WHERE publisher_name = 'National Textbook Company' LIMIT 1), '1992-01-01', NULL, 'eng', 884
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780844254821'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780844254821' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Donna Rosenberg' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780844254821' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Фёдор Михайлович Достоевский' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780844254821' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Антон Павлович Чехов' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780844254821' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Chinua Achebe' LIMIT 1), 4;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780844254821' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jorge Luis Borges' LIMIT 1), 5;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Guide to modern world literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780333427941', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780333427941'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780333427941' LIMIT 1), '9780333427941', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Papermac' LIMIT 1), '1973-01-01', NULL, 'eng', 1206
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780333427941'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780333427941' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Martin Seymour-Smith' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Prentice Hall Literature--Timeless Voices, Timeless Themes--World Literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780130508362', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780130508362'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780130508362' LIMIT 1), '9780130508362', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Prentice Hall' LIMIT 1), '2001-01-01', NULL, 'eng', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780130508362'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780130508362' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Carol Domblewski' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780130508362' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Chinua Achebe' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780130508362' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Anna Akhmatova' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780130508362' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Dante Alighieri' LIMIT 1), 4;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780130508362' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Isabel Allende' LIMIT 1), 5;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Masterpieces of world literature in digest form', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780060037505', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780060037505'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780060037505' LIMIT 1), '9780060037505', (SELECT publisher_id FROM publisher WHERE publisher_name = 'HarperCollins Publishers' LIMIT 1), '1952-01-01', NULL, 'eng', 1240
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780060037505'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780060037505' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Frank N. Magill' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Essentials of British and World Literature', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780030791796', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780030791796'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030791796' LIMIT 1), '9780030791796', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Holt Rinehart & Winston' LIMIT 1), '2006-01-01', NULL, 'eng', 1674
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780030791796'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030791796' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Kylene Beers' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030791796' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Chinua Achebe' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030791796' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Margaret Atwood' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030791796' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jorge Luis Borges' LIMIT 1), 4;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780030791796' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Антон Павлович Чехов' LIMIT 1), 5;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Lost World', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9798696445403', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9798696445403'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9798696445403' LIMIT 1), '9798696445403', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Babblebooks' LIMIT 1), '1900-01-01', NULL, 'ger,eng,spa', 238
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9798696445403'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798696445403' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Arthur Conan Doyle' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'November 9', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781508284987', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781508284987'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781508284987' LIMIT 1), '9781508284987', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Simon & Schuster' LIMIT 1), '2015-01-01', NULL, 'eng', 320
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781508284987'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781508284987' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Colleen Hoover' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Confess', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781476791456', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781476791456'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781476791456' LIMIT 1), '9781476791456', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Cengage Gale' LIMIT 1), '2015-01-01', NULL, 'tur,spa,eng', 320
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781476791456'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781476791456' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Colleen Hoover' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Hating Game', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780062439598', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780062439598'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780062439598' LIMIT 1), '9780062439598', (SELECT publisher_id FROM publisher WHERE publisher_name = 'PIATKUS' LIMIT 1), '2016-01-01', NULL, 'eng', 379
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780062439598'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780062439598' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Sally Thorne' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Drama', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9788417108588', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9788417108588'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9788417108588' LIMIT 1), '9788417108588', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Scholastic Canada, Limited' LIMIT 1), '2012-01-01', NULL, 'spa,fre,eng', 240
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9788417108588'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9788417108588' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Raina Telgemeier' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'The Spanish Love Deception', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9798705893843', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9798705893843'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9798705893843' LIMIT 1), '9798705893843', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Simon & Schuster Audio and Blackstone Publishing' LIMIT 1), '2021-01-01', NULL, 'eng', 480
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9798705893843'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9798705893843' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Elena Armas' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Haunted', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9788497934893', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9788497934893'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9788497934893' LIMIT 1), '9788497934893', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Random House Mondadori' LIMIT 1), '2005-01-01', NULL, 'eng,ita,spa', 432
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9788497934893'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9788497934893' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Chuck Palahniuk' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Maurice', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9782264012739', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9782264012739'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9782264012739' LIMIT 1), '9782264012739', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Alianza Editorial Sa' LIMIT 1), '1971-01-01', NULL, 'heb,eng,spa', 256
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9782264012739'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9782264012739' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'E. M. Forster' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Icebreaker', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9788466679299', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9788466679299'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9788466679299' LIMIT 1), '9788466679299', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Take university press' LIMIT 1), '2020-01-01', NULL, 'eng,spa', 448
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9788466679299'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9788466679299' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Hannah Grace' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Infinite Jest', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9783499249570', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9783499249570'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9783499249570' LIMIT 1), '9783499249570', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Quetzal' LIMIT 1), '1996-01-01', NULL, 'eng,ita,por', 1104
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9783499249570'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9783499249570' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'David Foster Wallace' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Middlesex', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9788467202281', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9788467202281'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9788467202281' LIMIT 1), '9788467202281', (SELECT publisher_id FROM publisher WHERE publisher_name = 'RBA' LIMIT 1), '2002-01-01', NULL, 'spa,ger,eng', 546
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9788467202281'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9788467202281' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Jeffrey Eugenides' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Push', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9781784877361', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9781784877361'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9781784877361' LIMIT 1), '9781784877361', (SELECT publisher_id FROM publisher WHERE publisher_name = 'VINTAGE' LIMIT 1), '1996-01-01', NULL, 'fre,spa,ger', 176
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9781784877361'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781784877361' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Sapphire' LIMIT 1), 1;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781784877361' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Tayari Jones' LIMIT 1), 2;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781784877361' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Sapphire' LIMIT 1), 3;
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9781784877361' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Sapphire, Lofton, Ramona' LIMIT 1), 4;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Post office', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780061492570', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780061492570'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780061492570' LIMIT 1), '9780061492570', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Ecco' LIMIT 1), '1974-01-01', NULL, 'rus,ger,eng', 160
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780061492570'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780061492570' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Charles Bukowski' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Eleven Minutes', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780061835575', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780061835575'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780061835575' LIMIT 1), '9780061835575', (SELECT publisher_id FROM publisher WHERE publisher_name = 'HarperCollins Publishers Australia' LIMIT 1), '2003-01-01', NULL, 'eng', 304
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780061835575'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780061835575' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Paulo Coelho' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Uprooted', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780804179034', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780804179034'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780804179034' LIMIT 1), '9780804179034', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Macmillan' LIMIT 1), '2015-01-01', NULL, 'eng', 438
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780804179034'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780804179034' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Naomi Novik' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Insomnia', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9785170178285', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9785170178285'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9785170178285' LIMIT 1), '9785170178285', (SELECT publisher_id FROM publisher WHERE publisher_name = 'AST' LIMIT 1), '1994-01-01', NULL, 'spa,eng,fre', 719
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9785170178285'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9785170178285' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Stephen King' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Ugly Love', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9788501105738', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9788501105738'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9788501105738' LIMIT 1), '9788501105738', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Galera Record' LIMIT 1), '2014-01-01', NULL, 'tur,por,eng', 344
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9788501105738'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9788501105738' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Colleen Hoover' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Little Fires Everywhere', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9783423147231', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9783423147231'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9783423147231' LIMIT 1), '9783423147231', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Penguin Publishing Group' LIMIT 1), '2014-01-01', NULL, 'ger,eng', 384
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9783423147231'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9783423147231' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Celeste Ng' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Daemon', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9780525951117', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9780525951117'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9780525951117' LIMIT 1), '9780525951117', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Penguin Audio' LIMIT 1), '2009-01-01', NULL, 'eng', 540
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9780525951117'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9780525951117' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Daniel Suarez' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Making Money', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9788499899657', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9788499899657'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9788499899657' LIMIT 1), '9788499899657', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Goldmann' LIMIT 1), '2007-01-01', NULL, 'eng,pol,ger', 400
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9788499899657'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9788499899657' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Terry Pratchett' LIMIT 1), 1;

INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status)
SELECT 'Purple Hibiscus', (SELECT category_id FROM category WHERE category_name = '文学' LIMIT 1), '本', 49.00, 31.85, '9788535918502', 'onsale'
WHERE NOT EXISTS (
  SELECT 1 FROM product WHERE barcode = '9788535918502'
);
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count)
SELECT (SELECT product_id FROM product WHERE barcode = '9788535918502' LIMIT 1), '9788535918502', (SELECT publisher_id FROM publisher WHERE publisher_name = 'Bonnier pocket' LIMIT 1), '2003-01-01', NULL, 'swe,spa,eng', 307
WHERE NOT EXISTS (
  SELECT 1 FROM book WHERE isbn = '9788535918502'
);
INSERT IGNORE INTO book_author (product_id, author_id, author_order)
SELECT (SELECT product_id FROM product WHERE barcode = '9788535918502' LIMIT 1), (SELECT author_id FROM author WHERE author_name = 'Chimamanda Ngozi Adichie' LIMIT 1), 1;
