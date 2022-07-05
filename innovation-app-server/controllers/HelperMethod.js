const jsonData = (data) =>{

    const files = COGFile(data);
    //const result = createJSON(files);

    return result
}

const COGFile = (data) =>{
    const arr = []

    data.map((element)=>{
        if(element.substring(0,4) === 'cogs'){
            if(element.length >= 30){
                arr.push(element.substring(24, element.length))
            }else{
                console.log(element.substring(5, element.length))
                arr.push(element.substring(5, element.length))
            }
        }
    })

    return arr
}

const createJSON = (files) =>{

    const arr1 = {
        files:[{
            id:'0',
            name:'COGS',
            COGS:[

            ],
        }]
    }
    var id = 0;

    files.map((element)=>{
        arr1.files[0].COGS.push({
            id:id.toString(),
            name:element,
            location:"https://innovation-netcdfs.s3.us-west-2.amazonaws.com/cogs/"+element,
        })
        id++;
    })

    return arr1
}

module.exports = {
    COGFile,
    jsonData
}