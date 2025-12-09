

const express = require('express')
const app = express()
const port = 3000

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html')
})

app.get('/', (req, res) => {
  res.send('Hello World!')
})


app.get('/hi' , (req , res) => {
  res.send(' hi there this is arya')
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})

// other people wont need node to run this application 
// if they hbave docker 


/// base iimage 
// FROM node:20
// WORKDIR /usr/src/app
// this is where i want to pull mycodebase
// COPY ..  -- copy all this file from 


// you should copy over the source code 
// always create .docker ignore file
// exposing a specific port 3000 
// containers are not always http servers
// 
// CMD["node" , "index.js"]
// before image gets loaded to container  run this 

// if i ever change my index.js file , 
// i need to run all the commands from top to again 
// from COPY , step will start changing 



