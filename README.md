# FoodReview

Discover where to eat in a new city, based on real dish-level reviews.

## Run locally
```
cp backend/.env.example backend/.env
docker compose up --build
```
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Frontend (React + Vite)
```
cd frontend
npm create vite@latest . -- --template react
npm install
npm run dev
```
