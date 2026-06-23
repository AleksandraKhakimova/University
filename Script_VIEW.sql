DROP VIEW IF EXISTS flights_tickets_sum_v20;

CREATE VIEW flights_tickets_sum_v20 AS
WITH bookings_summary AS (
  SELECT 
    f.flight_id,
    COUNT(t.ticket_no) AS tickets_count,
    SUM(tf.amount) AS tickets_sum,
    MAX(b.book_date)::date AS sale_end_date
  FROM flights_v f
  JOIN ticket_flights tf ON f.flight_id = tf.flight_id
  JOIN tickets t ON tf.ticket_no = t.ticket_no
  JOIN bookings b ON t.book_ref = b.book_ref
  GROUP BY f.flight_id
)
SELECT
  f.flight_id,
  f.departure_airport,
  f.arrival_airport,
  f.scheduled_departure::date AS scheduled_departure,
  f.scheduled_arrival::date AS scheduled_arrival,
  bs.tickets_count,
  bs.tickets_sum,
  bs.sale_end_date,
  ad.model->> 'en' AS aircraft_model
FROM flights_v f
LEFT JOIN bookings_summary bs ON f.flight_id = bs.flight_id
LEFT JOIN aircrafts_data ad ON f.aircraft_code = ad.aircraft_code
WHERE f.flight_id > 20;