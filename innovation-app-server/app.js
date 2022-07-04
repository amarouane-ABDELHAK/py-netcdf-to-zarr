const express = require('express');
const app = express();
const cors = require('cors')
require('dotenv').config()

const routes = require('./routes/index')

app.use(cors({
    origin:'*'
}))
app.use(express.json())

const PORT = 3056;


app.listen(PORT, console.log('Server Listening on PORT '+PORT+'...'))
app.use('/', routes)