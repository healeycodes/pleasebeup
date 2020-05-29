const fs = require('fs');

const setup = () => {
    const dbFile =
        process.env.NODE_ENV === 'test' ? './data/test.db' : './data/sqlite.db';
    const exists = fs.existsSync(dbFile);
    const sqlite3 = require('sqlite3').verbose();
    const db = new sqlite3.Database(dbFile);

    db.serialize(() => {
        if (!exists) {
            db.run(
                'CREATE TABLE User (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, sqltime DATETIME DEFAULT CURRENT_TIMESTAMP)'
            );
            console.log('New table User created!');

            db.run(
                'CREATE TABLE Website (id INTEGER PRIMARY KEY, email TEXT UNIQUE, url TEXT, up INTEGER, last_checked DATETIME, sqltime DATETIME DEFAULT CURRENT_TIMESTAMP)'
            );
            console.log('New table Website created!');
        }
    });
    return db;
};

module.exports = setup;
