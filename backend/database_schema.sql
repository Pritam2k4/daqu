-- DataReady AI Database Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    company_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data Sources table (uploaded files or database connections)
CREATE TABLE IF NOT EXISTS public.data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL CHECK (source_type IN ('file_upload', 'database_connection')),
    name TEXT NOT NULL,
    
    -- For file uploads
    file_path TEXT,
    file_size BIGINT,
    file_type TEXT,
    
    -- For database connections
    db_type TEXT,
    db_host TEXT,
    db_port INTEGER,
    db_name TEXT,
    
    -- Common fields
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quality Reports table
CREATE TABLE IF NOT EXISTS public.quality_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES public.data_sources(id) ON DELETE CASCADE,
    
    -- Quality scores
    overall_score NUMERIC(5,2),
    completeness_score NUMERIC(5,2),
    consistency_score NUMERIC(5,2),
    accuracy_score NUMERIC(5,2),
    
    -- Issues detected
    missing_values JSONB DEFAULT '{}',
    duplicates_count INTEGER DEFAULT 0,
    outliers JSONB DEFAULT '[]',
    type_mismatches JSONB DEFAULT '{}',
    
    -- Column-level insights
    column_insights JSONB DEFAULT '{}',
    
    -- Full report
    report_data JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Suggestions table
CREATE TABLE IF NOT EXISTS public.ai_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID NOT NULL REFERENCES public.quality_reports(id) ON DELETE CASCADE,
    
    issue_type TEXT NOT NULL,
    issue_description TEXT NOT NULL,
    suggested_fix TEXT NOT NULL,
    ai_explanation TEXT,
    confidence_score NUMERIC(3,2),
    
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'applied')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_at TIMESTAMP WITH TIME ZONE
);

-- Processing History table
CREATE TABLE IF NOT EXISTS public.processing_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES public.data_sources(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    action_type TEXT NOT NULL,
    transformations_applied JSONB DEFAULT '[]',
    suggestions_used JSONB DEFAULT '[]',
    
    before_stats JSONB,
    after_stats JSONB,
    
    status TEXT NOT NULL DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'failed')),
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Exports table
CREATE TABLE IF NOT EXISTS public.exports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES public.data_sources(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    export_format TEXT NOT NULL CHECK (export_format IN ('csv', 'json', 'parquet', 'excel')),
    file_url TEXT NOT NULL,
    file_size BIGINT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_data_sources_user_id ON public.data_sources(user_id);
CREATE INDEX IF NOT EXISTS idx_data_sources_created_at ON public.data_sources(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_quality_reports_source_id ON public.quality_reports(source_id);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_report_id ON public.ai_suggestions(report_id);
CREATE INDEX IF NOT EXISTS idx_processing_history_source_id ON public.processing_history(source_id);
CREATE INDEX IF NOT EXISTS idx_processing_history_user_id ON public.processing_history(user_id);

-- Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quality_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exports ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- Data sources policies
CREATE POLICY "Users can view own data sources" ON public.data_sources
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own data sources" ON public.data_sources
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own data sources" ON public.data_sources
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own data sources" ON public.data_sources
    FOR DELETE USING (auth.uid() = user_id);

-- Quality reports policies
CREATE POLICY "Users can view own quality reports" ON public.quality_reports
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.data_sources
            WHERE data_sources.id = quality_reports.source_id
            AND data_sources.user_id = auth.uid()
        )
    );

-- AI suggestions policies
CREATE POLICY "Users can view own AI suggestions" ON public.ai_suggestions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.quality_reports qr
            JOIN public.data_sources ds ON ds.id = qr.source_id
            WHERE qr.id = ai_suggestions.report_id
            AND ds.user_id = auth.uid()
        )
    );

-- Processing history policies
CREATE POLICY "Users can view own processing history" ON public.processing_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own processing history" ON public.processing_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Exports policies
CREATE POLICY "Users can view own exports" ON public.exports
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own exports" ON public.exports
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Functions and Triggers

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_sources_updated_at
    BEFORE UPDATE ON public.data_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create user profile
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();
