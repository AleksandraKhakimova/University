SELECT
    -- Итоги по дате: год, месяц, конкретный день
    EXTRACT(YEAR FROM f.scheduled_departure) AS flight_year,
    EXTRACT(MONTH FROM f.scheduled_departure) AS flight_month,
    EXTRACT(DAY FROM f.scheduled_departure) AS flight_day,
    f.scheduled_departure,
    -- Измерения для куба
    f.departure_airport,
    f.arrival_airport,
    f.flight_no,
    COUNT(t.ticket_no) AS tickets_count,
    SUM(tf.amount) AS total_ticket_amount
FROM flights_v f
    JOIN ticket_flights tf ON f.flight_id = tf.flight_id
    JOIN tickets t ON tf.ticket_no = t.ticket_no
GROUP BY
    ROLLUP (EXTRACT(YEAR FROM f.scheduled_departure),
            EXTRACT(MONTH FROM f.scheduled_departure),
            EXTRACT(DAY FROM f.scheduled_departure),
            f.scheduled_departure),
    CUBE (f.departure_airport,
          f.arrival_airport,
          f.flight_no)
ORDER BY flight_year, flight_month,flight_day, f.scheduled_departure;
