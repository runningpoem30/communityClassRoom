// Quick database connection test
const { Pool } = require('pg');

const pool = new Pool({
    connectionString: 'postgresql://postgres:postgres@localhost:5432/automaintainer'
});

async function test() {
    try {
        const res = await pool.query('SELECT COUNT(*) FROM agent_runs');
        console.log('✅ SUCCESS! Connected to database');
        console.log('   agent_runs count:', res.rows[0].count);
        process.exit(0);
    } catch (err) {
        console.error('❌ FAILED! Could not connect');
        console.error('   Error:', err.message);
        process.exit(1);
    }
}

test();
