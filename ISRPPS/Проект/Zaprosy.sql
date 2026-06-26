--Запросы--
--По номеру стс вывести все штрафы
SELECT f.*
FROM "Parkovki"."Fine" f
JOIN "Parkovki"."User" u ON f."STS" = u."STS"
WHERE u."STS" = 1;

--Количество автомобилей, зарегистрированных в каждом статусе (TRUE, FALSE)
SELECT "Status", COUNT(*) AS car_count 
FROM "Parkovki"."Bagration" 
GROUP BY "Status";