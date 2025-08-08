const sqlite3 = require('sqlite3').verbose();
const path = 'C:/Users/Not John Or Justin/Documents/instabids/cipher-data/cipher-sessions.db';

const db = new sqlite3.Database(path);

console.log('=== CHECKING CIPHER MEMORY DATABASE ===\n');

// Check all records in the database
db.all("SELECT key, LENGTH(value) as size FROM store", [], (err, rows) => {
    if (err) {
        console.error('Error querying database:', err);
        db.close();
        return;
    }
    
    console.log('Records in database:');
    rows.forEach(row => {
        console.log(`- ${row.key}: ${row.size} bytes`);
    });
    console.log(`\nTotal: ${rows.length} records\n`);
    
    // Now check for InstaBids content
    db.all("SELECT key, value FROM store", [], (err, rows) => {
        if (err) {
            console.error('Error:', err);
            db.close();
            return;
        }
        
        let instabidsCount = 0;
        let agentCount = 0;
        let deepagentsCount = 0;
        let tableCount = 0;
        
        rows.forEach(row => {
            const value = row.value.toLowerCase();
            if (value.includes('instabids')) instabidsCount++;
            if (value.includes('agent')) agentCount++;
            if (value.includes('deepagents')) deepagentsCount++;
            if (value.includes('60 tables') || value.includes('tables')) tableCount++;
        });
        
        console.log('Content analysis:');
        console.log(`- Records mentioning InstaBids: ${instabidsCount}`);
        console.log(`- Records mentioning agents: ${agentCount}`);
        console.log(`- Records mentioning deepagents: ${deepagentsCount}`);
        console.log(`- Records mentioning tables: ${tableCount}`);
        
        // Show a sample of what's stored
        console.log('\nSample content from first record:');
        if (rows.length > 0) {
            const sample = rows[0].value.substring(0, 500);
            console.log(sample + '...');
        }
        
        db.close();
    });
});