const express = require('express');
const session = require('express-session')
const SQLiteStore = require('connect-sqlite3')(session);
const nunjucks = require('nunjucks');
const app = express();

app.use(require('morgan')('combined'));
app.use(require('body-parser').urlencoded({ extended: true }));
app.use(session({
    store: new SQLiteStore,
    secret: 'your secret',
    cookie: { maxAge: 7 * 24 * 60 * 60 * 1000 },
    resave: false,
    saveUninitialized: false,
}));
app.use(express.static('templates'));
nunjucks.configure('templates', {
    autoescape: true,
    express: app,
    noCache: true,
});

const db = require('./db')();
const bcrypt = require('bcrypt');

const connectEnsureLogin = require('connect-ensure-login');
const passport = require('passport');
app.use(passport.initialize());
app.use(passport.session());
const LocalStrategy = require('passport-local').Strategy;

passport.use(new LocalStrategy({ usernameField: 'email', passwordField: 'password' },
    (email, password, done) => {
        db.all(
            'SELECT email, password FROM User WHERE email = (?)',
            [email],
            (err, rows) => {
                if (err) return done(null, false, { message: 'Server error.' });
                if (rows.length === 0) return done(null, false, { message: 'Username not found.' });
                bcrypt.compare(password, rows[0].password, (err, result) => {
                    if (result) {
                        return done(null, rows[0]);
                    }
                    done(null, false, { message: 'Incorrect password.' });
                });
            }
        );
    }
));

passport.serializeUser((user, cb) => {
    cb(null, user.email);
});

passport.deserializeUser((email, cb) => {
    db.all(
        'SELECT * FROM User WHERE email = (?)',
        [email],
        (err, rows) => {
            if (err) { return cb(err); }
            cb(null, rows[0]);
        }
    );
});

app.get('/', (request, response) => {
    response.render('home.html', { user: request.user });
});

app.get('/dashboard', connectEnsureLogin.ensureLoggedIn('/login'), (request, response) => {
    db.all('SELECT * from Website where email = ?', [request.user.email], (err, rows) => {
        if (err || rows.length === 0) return response.send('Server error.');
        response.render('dashboard.html', { website: rows[0], user: request.user });
    });
});

app.get('/login', (request, response) => {
    response.render('login.html');
});

app.post('/login',
    passport.authenticate('local', { failureRedirect: '/login', successRedirect: '/dashboard' }),
    (request, response) => {
        response.redirect('/dashboard');
    });

app.get('/logout',
    (request, response) => {
        request.logout();
        response.redirect('/');
    });

app.get('/register', (request, response) => {
    response.render('register.html');
});

app.post('/register', (request, response) => {
    bcrypt.hash(request.body.password, 10, (err, hash) => {
        db.serialize(() => {
            db.run(
                'INSERT INTO User (email, password) VALUES (?, ?)',
                [request.body.email, hash]
            );
            db.run(
                'INSERT INTO Website (email, url, failure_count, last_checked) VALUES (?, ?, ?, ?)',
                [request.body.email, request.body.website, 0, 0]
            );
        });
        passport.authenticate('local')(request, response, () => {
            response.redirect('/dashboard');
        });
    });
});

module.exports = {
    app: app,
    db: db
};