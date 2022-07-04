const jsonData = (data) =>{

    const files = COGFile(data);
    const result = createJSON(files);

    return result
}

const COGFile = (data) =>{
    const arr = []

    data.map((element)=>{
        if(element.substring(0,4) === 'cogs'){
            arr.push(element.substring(5, element.length))
        }
    })

    return arr
}

const createJSON = (files) =>{

    const arr1 = {
        files:[

        ]
    }
    var id = 0;

    files.map((element)=>{
        arr1.files.push({
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