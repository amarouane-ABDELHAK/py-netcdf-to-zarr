var rawData = [];
const sampleData = []

export function setData(data){
    console.log(data)
    data.files.map((element)=>{
        rawData.push(element)
    })

}

export function setDatasample(data){
    data.map((element)=>{
        rawData.push(element)
    })
}


export function getData(){
    return rawData
}

export function getFolders(){
    let foldernames = []
    console.log(rawData)
    rawData.map((element)=>{
        foldernames.push(element.name)
    })
    return foldernames
}

export function getCOGS(foldername){
    let COGS = []

    rawData.map((element)=>{
        if(element.name === foldername){

            COGS = element.COGS
        }
    })

    return COGS
}

export function getSingleCOG(foldername, id){

    let COG;

    for(var i = 0;i<rawData.length;i++){
        if(rawData[i].name === foldername){
            for(var j = 0;j<rawData[i].COGS.length;j++){
                if(rawData[i].COGS[j].id === id){
                    COG = rawData[i].COGS[j].API
                }
            }
        }
    }

    return [COG]
}