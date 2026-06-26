CREATE SCHEMA IF NOT EXISTS "Parkovki";  -- Создание схемы, если она не существует

-- Удаление таблиц, если они существуют (для избежания конфликтов при создании новых)
DROP TABLE IF EXISTS "Parkovki"."Session" CASCADE;
DROP TABLE IF EXISTS "Parkovki"."Benefits_Parkovki" CASCADE;
DROP TABLE IF EXISTS "Parkovki"."User" CASCADE;
DROP TABLE IF EXISTS "Parkovki"."TroikaCard" CASCADE;
DROP TABLE IF EXISTS "Parkovki"."TollRoads" CASCADE;
DROP TABLE IF EXISTS "Parkovki"."Parkovki" CASCADE;
DROP TABLE IF EXISTS "Parkovki"."MCD" CASCADE;
DROP TABLE IF EXISTS "Parkovki"."Fine" CASCADE;
DROP TABLE IF EXISTS "Parkovki"."Benefits" CASCADE;
DROP TABLE IF EXISTS "Parkovki"."Bagration" CASCADE;

-- Создание таблицы Session
CREATE TABLE IF NOT EXISTS "Parkovki"."Session" (
    id integer NOT NULL,
    "Phone_Number" character varying(255) NOT NULL,
    "Car" character varying(255) NOT NULL,
	"Date_time" timestamp NOT NULL,
	"Zone_Number" character varying(255) NOT NULL,
	id_parkovki integer,
    CONSTRAINT "Session_pkey" PRIMARY KEY (id)  -- Установка первичного ключа
);

-- Создание таблицы Bagration
CREATE TABLE IF NOT EXISTS "Parkovki"."Bagration" (
    id integer NOT NULL,
    "UIN" integer NOT NULL,
	"Car" character varying(255) NOT NULL,
    "Status" boolean NOT NULL,
    "Date" character varying(255) NOT NULL,
    CONSTRAINT "Bagration_pkey" PRIMARY KEY (id)  -- Установка первичного ключа
);

-- Создание таблицы Benefits
CREATE TABLE IF NOT EXISTS "Parkovki"."Benefits" (
    id integer NOT NULL,
    "District" character varying(255) NOT NULL,
    "Number" character varying(255) NOT NULL,
    "Validity_Period" character varying(255) NOT NULL,
    CONSTRAINT "Benefits_pkey" PRIMARY KEY (id)  -- Установка первичного ключа
);

-- Создание таблицы Fine
CREATE TABLE IF NOT EXISTS "Parkovki"."Fine" (
    id integer NOT NULL,
    "UIN" integer NOT NULL,
	"STS" integer NOT NULL,
	"Date_Time" character varying(255) NOT NULL,
    "Status" boolean NOT NULL,
    "Sum" integer NOT NULL,
    CONSTRAINT "Fine_pkey" PRIMARY KEY (id)  -- Установка первичного ключа
);

-- Создание таблицы MCD
CREATE TABLE IF NOT EXISTS "Parkovki"."MCD" (
    id integer NOT NULL,
    "Status" boolean NOT NULL,
    "UIN" integer NOT NULL,
    "Date" character varying(255) NOT NULL,
    CONSTRAINT "MCD_pkey" PRIMARY KEY (id)  -- Установка первичного ключа
);

-- Создание таблицы Parkovki
CREATE TABLE IF NOT EXISTS "Parkovki"."Parkovki" (
    id integer NOT NULL,
    "Zone_Number" character varying(255) NOT NULL,
    "Number_of_seats" integer NOT NULL,
    "Cost" character varying(255) NOT NULL,
    "Invalide" boolean NOT NULL,
    CONSTRAINT "Parkovki_pkey" PRIMARY KEY (id)  -- Установка первичного ключа
);

-- Создание таблицы TollRoads
CREATE TABLE IF NOT EXISTS "Parkovki"."TollRoads" (
    id integer NOT NULL,
    "idMCD" integer NOT NULL,
    "idBagration" integer NOT NULL,
    "id_MCD" integer,
    "id_Bagration" integer,
    CONSTRAINT "TollRoads_pkey" PRIMARY KEY (id)  -- Установка первичного ключа
);

-- Создание таблицы TroikaCard
CREATE TABLE IF NOT EXISTS "Parkovki"."TroikaCard" (
    id integer NOT NULL,
    "Balance" integer NOT NULL,
    "Number" integer NOT NULL,
    "Validity_Period" character varying(255) NOT NULL,
    CONSTRAINT "TroikaCard_pkey" PRIMARY KEY (id)  -- Установка первичного ключа
);

-- Создание таблицы User
CREATE TABLE IF NOT EXISTS "Parkovki"."User" (
    "id_user" integer NOT NULL,
    "Name" character varying(255) NOT NULL,
    "Phone_Number" character varying(255) NOT NULL,
    "Car" character varying(255),
    "Email" character varying(255),
    "STS" integer,
	id_parkovki integer,
    id_benefits integer,
    id_fine integer,
    id_troika integer,
    id_tollroads integer,
	id_session integer,
    CONSTRAINT "User_pkey" PRIMARY KEY ("id_user")  -- Установка первичного ключа
);

-- Создание промежуточной таблицы для связи Benefits и Parkovki
CREATE TABLE IF NOT EXISTS "Parkovki"."Benefits_Parkovki" (
    "Benefits_id" integer NOT NULL,
    "Parkovki_id" integer NOT NULL
);

-- Добавление внешних ключей с каскадными действиями (UPDATE CASCADE, DELETE SET NULL)

-- Внешний ключ для связи с таблицей MCD, каскадное обновление и установка NULL при удалении
ALTER TABLE IF EXISTS "Parkovki"."TollRoads"
    ADD CONSTRAINT "MCD_fkey" FOREIGN KEY ("id_MCD")
    REFERENCES "Parkovki"."MCD" (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL;


-- Внешний ключ для связи с таблицей Bagration, каскадное обновление и установка NULL при удалении
ALTER TABLE IF EXISTS "Parkovki"."TollRoads"
    ADD CONSTRAINT "Bagration_fkey" FOREIGN KEY ("id_Bagration")
    REFERENCES "Parkovki"."Bagration" (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL;

-- Внешний ключ для связи с таблицей Session, каскадное обновление и установка NULL при удалении
ALTER TABLE IF EXISTS "Parkovki"."User"
    ADD CONSTRAINT session_fkey FOREIGN KEY (id_session)
    REFERENCES "Parkovki"."Session" (id)
    ON UPDATE CASCADE
    ON DELETE CASCADE;
    

-- Внешний ключ для связи с таблицей Parkovki, каскадное обновление и установка NULL при удалении
ALTER TABLE "Parkovki"."Session"
ADD CONSTRAINT parkovki_fkey FOREIGN KEY (id_parkovki) REFERENCES "Parkovki"."Parkovki"(id);


-- Внешний ключ для связи с таблицей Fine, каскадное обновление и установка NULL при удалении
ALTER TABLE IF EXISTS "Parkovki"."User"
    ADD CONSTRAINT fine_fkey FOREIGN KEY (id_fine)
    REFERENCES "Parkovki"."Fine" (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL;

-- Внешний ключ для связи с таблицей TroikaCard, каскадное обновление и установка NULL при удалении
ALTER TABLE IF EXISTS "Parkovki"."User"
    ADD CONSTRAINT troika_fkey FOREIGN KEY (id_troika)
    REFERENCES "Parkovki"."TroikaCard" (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL;

-- Внешний ключ для связи с таблицей Benefits, каскадное обновление и установка NULL при удалении
ALTER TABLE IF EXISTS "Parkovki"."User"
    ADD CONSTRAINT benefits_fkey FOREIGN KEY (id_benefits)
    REFERENCES "Parkovki"."Benefits" (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL;

-- Внешний ключ для связи с таблицей TollRoads, каскадное обновление и установка NULL при удалении
ALTER TABLE IF EXISTS "Parkovki"."User"
    ADD CONSTRAINT tollroads_fkey FOREIGN KEY (id_tollroads)
    REFERENCES "Parkovki"."TollRoads" (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL;

-- Внешний ключ для связи с таблицей Benefits в промежуточной таблице Benefits_Parkovki
ALTER TABLE IF EXISTS "Parkovki"."Benefits_Parkovki"
    ADD FOREIGN KEY ("Benefits_id")
    REFERENCES "Parkovki"."Benefits" (id)
    ON UPDATE CASCADE
    ON DELETE CASCADE;

-- Внешний ключ для связи с таблицей Parkovki в промежуточной таблице Benefits_Parkovki
ALTER TABLE IF EXISTS "Parkovki"."Benefits_Parkovki"
    ADD FOREIGN KEY ("Parkovki_id")
    REFERENCES "Parkovki"."Parkovki" (id)
    ON UPDATE CASCADE
    ON DELETE CASCADE;


	


