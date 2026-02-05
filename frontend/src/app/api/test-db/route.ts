import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
    try {
        const result = await query('SELECT NOW() as time, current_user as db_user');
        return NextResponse.json({
            ok: true,
            connection: 'SUCCESS',
            ...result.rows[0]
        });
    } catch (error: any) {
        return NextResponse.json({
            ok: false,
            connection: 'FAILED',
            error: error.message,
            code: error.code,
            detail: error.detail,
        }, { status: 500 });
    }
}
