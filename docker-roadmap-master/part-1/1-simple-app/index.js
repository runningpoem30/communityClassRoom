

const express = require('express')
const app = express()
const port = 3000

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html')
})

app.get('/', (req, res) => {
  res.send('Hello World!')
})


app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})


/// u still have auxillary sevices running on your machine 
/// running a sinlge command , you can bring all the services on your machine 
/// clean out ur machine !! 