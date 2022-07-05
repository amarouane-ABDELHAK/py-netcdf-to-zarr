const aws = require('aws-sdk')
aws.config.setPromisesDependency();
aws.config.update({
    profile:process.env.AWS_PROFILE,
    region:'us-west-2'
})

const Help = require('./HelperMethod')

const s3 = new aws.S3()


async function getData(){
    var params = {
        Bucket: 'innovation-netcdfs'    
    };
    
    try{
        const results = await s3.listObjectsV2(params).promise().then(data => {
            const arr = []
            data.Contents.map((element)=>{
                arr.push(element.Key)
            })
            //console.log(arr)
            return Help.jsonData(arr)
        }).catch(function (err) {
            console.warn('Not exist folder exception is not catch here!' );
            return false;
        });
        return results;
    }catch{
        console.warn('Errorrrr')
        return false
    }
}

module.exports = {
    getData
}