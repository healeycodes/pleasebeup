const { app } = require('./app');

const listener = app.listen(process.env.PORT, () => {
    const port = listener.address().port;
    console.log(
        `pleasebeup listening on port: ${port}\n\nClick me if you're DEVing: http://localhost:${port}`
    );
});