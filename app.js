const express = require('express');
const bodyParser = require('body-parser');
const nunjucks = require('nunjucks');
const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('templates'));
nunjucks.configure('templates', {
    autoescape: true,
    express: app,
    noCache: true,
});

const db = require('./db')();
const bcrypt = require('bcrypt');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;

passport.use(new LocalStrategy(
    function (username, password, done) {
        db.all(
            'SELECT email, password FROM User WHERE email = (?)',
            [username],
            (err, rows) => {
                if (err) return done(null, false, { message: 'Server error.' });
                if (rows.length === 0) return done(null, false, { message: 'Username not found.' });
                bcrypt.compare(password, rows[0].password, function (err, result) {
                    if (result) {
                        return done(null, user);
                    }
                    return done(null, false, { message: 'Incorrect password.' });
                });
            }
        );
    }
));

app.get('/', (request, response) => {
    response.render('index.html');
});

app.get('/dashboard', passport.authenticate('local', { failureRedirect: '/login' }), (request, response) => {
    response.render('dashboard.html');
});

app.get('/register', (request, response) => {
    response.render('register.html');
});

app.post('/register', (request, response) => {
    bcrypt.hash(request.body.password, 10, function(err, hash) {
        db.serialize(() => {
            db.run(
                'INSERT INTO User (email, password) VALUES (?, ?)',
                [request.body.email, hash]
            );
            db.run(
                'INSERT INTO Website (email, url) VALUES (?, ?)',
                [request.body.email, request.body.url]
            );
        });
        return response.redirect('/dashboard')
    });
});

module.exports = {
    app: app,
    db: db
};