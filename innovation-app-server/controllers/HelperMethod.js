const COGFile = (data) =>{
    const arr = []

    data.map((element)=>{
        if(element.substring(0,4) === 'cogs'){
            arr.push(element.substring(5, element.length))
        }
    })

    return arr
}

const isCorrectFolder = (data, foldername) =>{

}


module.exports = {
    COGFile
}