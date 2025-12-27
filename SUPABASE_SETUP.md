# Setting Up Supabase Database

Follow these steps to set up your Supabase database for DataReady AI.

## 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in:
   - **Project name**: dataready-ai
   - **Database password**: (create a strong password)
   - **Region**: Choose closest to you
5. Wait for project to be created (~2 minutes)

## 2. Get Your Credentials

1. In your Supabase project dashboard
2. Go to **Settings** → **API**
3. Copy these values:
   - **Project URL** (looks like: `https://xxx.supabase.co`)
   - **anon/public key** (long string starting with `eyJ...`)

## 3. Update Backend .env File

Create/update `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
```

## 4. Run Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy the entire contents of `backend/database_schema.sql`
4. Paste into the SQL editor
5. Click "Run"
6. You should see "Success. No rows returned"

This creates all tables:
- `users`
- `data_sources`
- `quality_reports`
- `ai_suggestions`
- `processing_history`
- `exports`

## 5. Verify Tables Created

1. Go to **Table Editor** in Supabase
2. You should see all 6 tables listed
3. Click on each to verify structure

## 6. Enable Authentication (Optional for now)

1. Go to **Authentication** → **Providers**
2. Enable **Google** provider
3. Add authorized redirect URLs:
   - `http://localhost:5173`
   - `http://localhost:8000`

## 7. Test Connection from Backend

Restart your backend server and visit:
```
http://localhost:8000/api/v1/database/test
```

You should see:
```json
{
  "connected": true,
  "message": "Connected successfully. Users count: 0",
  "database": "Supabase PostgreSQL"
}
```

## 8. Update Frontend .env

Create/update `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here
```

## Troubleshooting

### Connection Failed
- Check `.env` file has correct SUPABASE_URL and SUPABASE_KEY
- Verify credentials from Supabase dashboard
- Ensure no extra spaces or quotes in .env values

### Tables Not Created
- Run the SQL schema again
- Check SQL Editor for error messages
- Verify you're running it in the correct project

### RLS Policies Too Restrictive
- For development, you can temporarily disable RLS:
  ```sql
  ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
  ```
  (Re-enable before production!)

## Database Schema Overview

```
users (extends auth.users)
  ├─ data_sources (files or DB connections)
  │   ├─ quality_reports
  │   │   └─ ai_suggestions
  │   ├─ processing_history
  │   └─ exports
```

## Next Steps

After database is set up:
1. Implement file upload storage
2. Add user authentication
3. Build data quality analysis
4. Create AI suggestions engine
