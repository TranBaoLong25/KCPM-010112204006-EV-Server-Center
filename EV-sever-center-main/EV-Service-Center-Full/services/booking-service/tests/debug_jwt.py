import os
from app import create_app
from flask_jwt_extended import create_access_token

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['JWT_SECRET_KEY'] = 'test-secret'
os.environ['INTERNAL_SERVICE_TOKEN'] = 'test-internal-token'
os.environ['USER_SERVICE_URL'] = 'http://localhost'

app = create_app()
with app.test_client() as client:
    token = create_access_token(identity=1, additional_claims={'role': 'user'})
    resp = client.post(
        '/api/bookings/items',
        json={
            'service_type': 'Bảo dưỡng ắc quy',
            'technician_id': 2,
            'station_id': 3,
            'start_time': '2026-07-01T08:00:00',
            'end_time': '2026-07-01T09:00:00'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    print('status', resp.status_code)
    print('body', resp.get_data(as_text=True))
