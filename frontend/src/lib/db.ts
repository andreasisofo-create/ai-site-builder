import { Pool } from 'pg';

// DIRECT CONNECTION (for Vercel serverless - no Static IP needed)
const user = 'postgres.xdnpsxjjaupmxocjkngt';
const password = encodeURIComponent('E-quipe!12345'); // ! → %21
const host = 'db.xdnpsxjjaupmxocjkngt.supabase.co'; // Direct connection host
const port = 5432; // Direct connection port (not pooler 6543)
const database = 'postgres';

const connectionString = `postgresql://${user}:${password}@${host}:${port}/${database}`;

export const pool = new Pool({
    connectionString,
    ssl: { rejectUnauthorized: false },
    connectionTimeoutMillis: 10000,
    max: 1, // Serverless: 1 connection per function invocation
});

// Helper for queries (works with both pooler and direct)
export async function query(text: string, params?: any[]) {
    const client = await pool.connect();
    try {
        const result = await client.query({
            text,
            values: params,
        });
        return result;
    } catch (error: any) {
        console.error('[DB ERROR]', {
            message: error.message,
            code: error.code,
            detail: error.detail,
        });
        throw error;
    } finally {
        client.release();
    }
}
