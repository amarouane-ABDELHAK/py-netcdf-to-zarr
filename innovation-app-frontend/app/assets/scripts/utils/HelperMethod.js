import data from "../components/pages/data"

export const filetoJSON = (filename) =>{
    const arr = {
        files:[{
            id:'0',
            name:'COGS',
            COGS:[

            ],
        }]
    }

    arr.files[0].COGS.push()


    filename.map((element)=>{
        arr.files[0].COGS.push(findElement(element))
    })

    return arr
}

const findElement = (name) =>{

    for(var i = 0;i<data.files.length;i++){
        for(var j = 0;j<data.files[i].COGS.length;j++){
            if(data.files[i].COGS[j].name === name){
                return data.files[i].COGS[j]
            }
        }
    }

    return {
        id:Math.random().toString(),
        name:name,
        API:'https://3ckzasvsu4.execute-api.us-west-2.amazonaws.com/development/singleband/VHRFC/LIS/FRD/{z}/{x}/{y}.png?colormap=terrain&stretch_range=[0.32524657249450684,23.42554473876953]',
        location:'https://innovation-netcdfs.s3.us-west-2.amazonaws.com/cogs/VHRFC_LIS_FRD_co.tif',
        thumbnailURL:''
    }
}