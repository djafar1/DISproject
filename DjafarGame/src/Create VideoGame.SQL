CREATE TABLE IF NOT EXISTS video_games (
    Title VARCHAR(255),
    ReleaseDate DATE,
    Developer VARCHAR(255),
    Publisher VARCHAR(255),
    Genres VARCHAR(100),
    ProductRating VARCHAR(100),
    UserScore FLOAT,
    UserRatingsCount INT
);

-- REPLACE FROM with your own direct path to csv file in TMP.
\copy video_games(Title, ReleaseDate, Developer, Publisher, Genres, ProductRating, UserScore, UserRatingsCount) from 'C:\Users\djafa\OneDrive\Skrivebord\DIS\DISproject\DjafarGame\nft-crypto-punk\tmp\videogames.csv' delimiter ',' CSV HEADER;