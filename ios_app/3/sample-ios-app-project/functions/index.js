const functions = require('firebase-functions');

exports.helloWorld = functions.https.onRequest(
    (request, response) => {
        response.send({
            data: "Hello from Firebase Cloud Functions!"
        })
    }
);