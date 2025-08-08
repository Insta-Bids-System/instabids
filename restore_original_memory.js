const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');

// Read from the original database with all the InstaBids history
const originalDB = 'C:/Users/Not John Or Justin/data/cipher-sessions.db';

const db = new sqlite3.Database(originalDB);

console.log('=== EXTRACTING ORIGINAL INSTABIDS MEMORIES ===\n');

// Extract all the important InstaBids-related conversations
const queries = [
    "SELECT value FROM store WHERE key = 'messages:deepagents_supabase_expert'",
    "SELECT value FROM store WHERE key = 'messages:supabase_expert_onboarding'",
    "SELECT value FROM store WHERE key = 'messages:deepagents_orchestrator'",
    "SELECT value FROM store WHERE key = 'messages:deepagents_orchestrator_complete'",
    "SELECT value FROM store WHERE key = 'cipher:sessions:default'"
];

const memories = [];

let completed = 0;
queries.forEach((query, index) => {
    db.get(query, [], (err, row) => {
        if (err) {
            console.error('Error:', err);
        } else if (row) {
            try {
                const data = JSON.parse(row.value);
                
                // Extract meaningful content
                if (data.conversationHistory) {
                    data.conversationHistory.forEach(msg => {
                        if (msg.content && msg.content[0] && msg.content[0].text) {
                            const text = msg.content[0].text;
                            if (text.includes('InstaBids') || text.includes('agent') || text.includes('database')) {
                                memories.push(text.substring(0, 1000));
                            }
                        }
                    });
                } else if (Array.isArray(data)) {
                    data.forEach(msg => {
                        if (msg.content && msg.content[0] && msg.content[0].text) {
                            const text = msg.content[0].text;
                            if (text.includes('InstaBids') || text.includes('Supabase')) {
                                memories.push(text.substring(0, 1000));
                            }
                        }
                    });
                }
            } catch (e) {
                console.log('Could not parse:', query);
            }
        }
        
        completed++;
        if (completed === queries.length) {
            console.log(`Found ${memories.length} memory fragments\n`);
            
            // Save to file for reference
            const output = memories.join('\n\n---\n\n');
            fs.writeFileSync('extracted_memories.txt', output);
            console.log('Memories saved to extracted_memories.txt');
            
            // Show sample
            console.log('\nSample memories found:');
            memories.slice(0, 3).forEach((mem, i) => {
                console.log(`\nMemory ${i+1}:`);
                console.log(mem.substring(0, 200) + '...');
            });
            
            db.close();
        }
    });
});