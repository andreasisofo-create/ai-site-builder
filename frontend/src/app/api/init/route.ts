import { NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
        rejectUnauthorized: false
    }
});

export async function GET() {
    try {
        const client = await pool.connect();
        try {
            await client.query(`
        -- Tabella Utenti
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR UNIQUE NOT NULL,
            hashed_password VARCHAR,
            full_name VARCHAR,
            avatar_url VARCHAR,
            oauth_provider VARCHAR,
            oauth_id VARCHAR UNIQUE,
            is_active BOOLEAN DEFAULT TRUE,
            is_superuser BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Tabella Siti (già che ci siamo, prepariamo il terreno)
        CREATE TABLE IF NOT EXISTS sites (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            title VARCHAR NOT NULL,
            slug VARCHAR UNIQUE,
            description TEXT,
            status VARCHAR DEFAULT 'draft',
            settings JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
      `);
            return NextResponse.json({ message: "Database tables created successfully!" });
        } finally {
            client.release();
        }
    } catch (error) {
        return NextResponse.json({ error: String(error) }, { status: 500 });
    }
}
