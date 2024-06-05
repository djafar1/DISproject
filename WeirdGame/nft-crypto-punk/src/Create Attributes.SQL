CREATE TABLE IF NOT EXISTS Attributes(id char(4),
type char(20),
gender char(20),
skin_tone char(30),
count int,
accessories char(10000),
CONSTRAINT nft_pk PRIMARY KEY (id));

copy  Attributes(id,type,gender, skin_tone, count, accessories)
            from 'C:\PATH\TO\PROJECT\dis-nft-project\tmp\attributes.csv'
            delimiter ','
            CSV HEADER;
