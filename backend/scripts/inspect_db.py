from app.db.database import SessionLocal
from app.models.user import User
from app.models.booking import Booking

session = SessionLocal()
try:
    users = session.query(User).all()
    print('USERS', len(users))
    for u in users:
        print(str(u.id), u.email, 'admin' if u.is_admin else 'provider' if u.is_provider else 'customer')
    bookings = session.query(Booking).all()
    print('BOOKINGS', len(bookings))
    for b in bookings:
        print(str(b.id), str(b.customer_id), b.status, b.booking_date, b.booking_time, b.town)
finally:
    session.close()
