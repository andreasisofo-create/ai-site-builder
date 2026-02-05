import { Pool } from 'pg';

// Costruisci la connection string con password encodata
const user = 'postgres.xdnpsxjjaupmxocjkngt';
const password = encodeURIComponent('E-quipe!12345'); // ! → %21
const host = 'aws-1-eu-west-1.pooler.supabase.com';
const port = 6543;
const database = 'postgres';

const connectionString = `postgresql://${user}:${password}@${host}:${port}/${database}`;

export const pool = new Pool({
    connectionString,
    ssl: { rejectUnauthorized: false },
    // PgBouncer transaction mode configs
    connectionTimeoutMillis: 10000,
    max: 5, // Keep pool small for serverless
});

// Helper per query senza prepared statements (fondamentale per PgBouncer)
export async function query(text: string, params?: any[]) {
    const client = await pool.connect();
    try {
        // Si noti l'uso di un oggetto query senza 'name' per evitare prepared statements
        const result = await client.query({
            text,
            values: params,
            // rowMode: undefined (default)
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
