# KaziLink Frontend

React + Vite frontend for the existing KaziLink FastAPI/PostgreSQL backend.

## Run

1. Start FastAPI on `http://127.0.0.1:8000`.
2. Open this `frontend` folder in VS Code.
3. Run `npm install`.
4. Run `npm run dev`.
5. Open `http://localhost:5173`.

The Vite development server proxies `/api/*` to the FastAPI backend, so local development does not require a CORS change.

## Existing backend endpoints used

- `/auth/register/customer`
- `/auth/login`
- `/users/me`
- `/categories`
- `/providers/search`
- `/providers/{id}`
- `/providers/apply`
- `/providers/me`
- `/providers/me/services`
- `/providers/me/location`
- `/providers/me/service-radius`
- `/providers/{id}/availability`
- `/bookings`
- `/bookings/customer/me`
- `/bookings/provider/me`
- `/reviews`
- `/reviews/provider/{id}`
- `/admin/providers`
- `/admin/providers/pending`
- `/admin/providers/{id}`
- `/admin/users`

## Integration gaps found in the supplied backend

1. Public provider responses do not include the provider user's first/last name. The UI therefore uses a neutral provider label until the backend exposes the name.
2. There is no endpoint for uploading/updating national ID or good-conduct documents.
3. There is no admin-wide bookings endpoint, so the admin UI does not invent one.
4. Provider profile editing currently exposes location and service-radius updates, but not general edits to bio, rates, town or experience.
5. The supplied availability endpoints are not protected by the current-user/provider dependency. This should be fixed before deployment.
