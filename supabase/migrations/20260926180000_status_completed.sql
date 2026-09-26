-- Frontend and UX Plan v2 (H.4): information-only tasks can finish successfully without a booking.
-- ALTER TYPE ... ADD VALUE must run in its own migration (not usable in the same transaction).
alter type request_status add value if not exists 'completed';
