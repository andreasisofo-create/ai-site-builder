import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import bcrypt from 'bcryptjs';

export async function POST(req: Request) {
    try {
        const { email, password, fullName } = await req.json();

        if (!email || !password || !fullName) {
            return NextResponse.json(
                { message: 'Mancano dei campi obbligatori' },
                { status: 400 }
            );
        }

        // Checking if user already exists
        const existingUser = await query('SELECT id FROM users WHERE email = $1', [email]);
        if (existingUser.rows.length > 0) {
            return NextResponse.json(
                { message: 'Utente già registrato' },
                { status: 409 }
            );
        }

        // Hashing password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Creating user
        const result = await query(
            `INSERT INTO users (email, hashed_password, full_name, is_active, created_at, updated_at)
       VALUES ($1, $2, $3, $4, NOW(), NOW())
       RETURNING id, email, full_name`,
            [email, hashedPassword, fullName, true]
        );

        return NextResponse.json(
            { message: 'Utente creato con successo', user: result.rows[0] },
            { status: 201 }
        );
    } catch (error: any) {
        console.error('Registration Error:', error);
        return NextResponse.json(
            { message: 'Errore durante la registrazione', error: error.message },
            { status: 500 }
        );
    }
}
