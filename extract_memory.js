const sqlite3 = require('sqlite3').verbose();
const path = 'C:/Users/Not John Or Justin/data/cipher-sessions.db';

const db = new sqlite3.Database(path);

console.log('=== EXTRACTING ALL INSTABIDS MEMORY DATA ===\n');

// Get ALL memory records that mention InstaBids
db.all("SELECT key, value FROM store WHERE value LIKE '%instabids%' OR value LIKE '%InstaBids%' OR key LIKE '%instabids%'", [], (err, rows) => {
    if (err) {
        console.error('Error querying InstaBids data:', err);
        db.close();
        return;
    }
    
    console.log(`Found ${rows.length} records with InstaBids mentions:\n`);
    
    rows.forEach((row, index) => {
        console.log(`\n=== MEMORY RECORD ${index + 1} ===`);
        console.log('Key:', row.key);
        
        try {
            const data = JSON.parse(row.value);
            
            // If it's a conversation, extract the relevant parts
            if (data.conversationHistory) {
                console.log('Type: Full Session Data');
                data.conversationHistory.forEach((msg, i) => {
                    if (JSON.stringify(msg).toLowerCase().includes('instabids')) {
                        console.log(`\nMessage ${i}:`, msg.role);
                        if (msg.content && msg.content[0] && msg.content[0].text) {
                            const text = msg.content[0].text;
                            if (text.toLowerCase().includes('instabids')) {
                                console.log('Content:', text.substring(0, 500));
                            }
                        }
                    }
                });
            } else if (Array.isArray(data)) {
                console.log('Type: Message Array');
                data.forEach(msg => {
                    if (JSON.stringify(msg).toLowerCase().includes('instabids')) {
                        console.log('Message:', JSON.stringify(msg, null, 2).substring(0, 500));
                    }
                });
            } else {
                console.log('Type: Other');
                console.log('Data:', JSON.stringify(data, null, 2).substring(0, 500));
            }
        } catch (e) {
            console.log('Raw value:', row.value.substring(0, 500));
        }
    });
    
    // Also get the main session data
    db.all("SELECT value FROM store WHERE key = 'cipher:sessions:default'", [], (err, sessionRows) => {
        if (err) {
            console.error('Error getting session:', err);
        } else if (sessionRows.length > 0) {
            console.log('\n\n=== MAIN SESSION DATA ===');
            try {
                const session = JSON.parse(sessionRows[0].value);
                if (session.conversationHistory) {
                    console.log(`Total conversation messages: ${session.conversationHistory.length}`);
                    
                    // Find InstaBids-related messages
                    session.conversationHistory.forEach((msg, i) => {
                        const msgStr = JSON.stringify(msg);
                        if (msgStr.toLowerCase().includes('instabids') || 
                            msgStr.toLowerCase().includes('agent') ||
                            msgStr.toLowerCase().includes('database')) {
                            console.log(`\n--- Message ${i} (${msg.role}) ---`);
                            if (msg.content && msg.content[0] && msg.content[0].text) {
                                console.log(msg.content[0].text.substring(0, 300) + '...');
                            }
                        }
                    });
                }
            } catch (e) {
                console.log('Could not parse session data');
            }
        }
        
        db.close();
        console.log('\n=== EXTRACTION COMPLETE ===');
    });
});