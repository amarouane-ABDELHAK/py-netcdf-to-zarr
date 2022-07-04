const express = require('express')
const router = express.Router();
const controller = require('../controllers/index')

router.route('/data').get(async(req, res)=>{
    try{
        const data = await controller.getData();
        console.log(data)
        res.status(200).json(data)
    }catch{
        res.status(500).json('Error')
    }
})

module.exports = router