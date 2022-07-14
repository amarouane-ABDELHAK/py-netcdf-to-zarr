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

    const title = name.slice(0,5)
    var number;

    var index = 23;
    var name2 = "VHRMC_LIS_FRD_Month_445.0_co.tif"

    if(name !== 'VHRFC_LIS_FRD_co.tif'){
        for(var i = 0;i<5;i++){
            if(name.slice(index, index+1) === '_'){
                number = name.slice(20, index)
                break;
            }else{
                index = index + 1;
            }
        }
    }
    
    var API;
    var location;

    if(title === 'VHRFC'){
        API = "https://3ckzasvsu4.execute-api.us-west-2.amazonaws.com/development/singleband/VHRFC/201301/LIS/{z}/{x}/{y}.png?colormap=terrain&stretch_range=[0.32524657249450684,23.42554473876953]"
        location = "https://innovation-netcdfs.s3.us-west-2.amazonaws.com/cogs/VHRFC_LIS_FRD_co.tif"
    }else if(title === 'VHRMC'){
        API = "https://3ckzasvsu4.execute-api.us-west-2.amazonaws.com/development/singleband/VHRMC/"+number+"/LIS/{z}/{x}/{y}.png?colormap=terrain&stretch_range=[0.00004769196311826818,0.06768383830785751]"
        location = "https://innovation-netcdfs.s3.us-west-2.amazonaws.com/cogs/VHRMC_LIS_FRD_cogs/VHRMC_LIS_FRD_Month_"+number+"_co.tif"
    }else if(title === 'VHRDC'){
        API = "https://3ckzasvsu4.execute-api.us-west-2.amazonaws.com/development/singleband/VHRDC/"+number+"/LIS/{z}/{x}/{y}.png?colormap=terrain&stretch_range=[0.000010303672752343118,0.0022336216643452644]"
        location = "https://innovation-netcdfs.s3.us-west-2.amazonaws.com/cogs/VHRDC_LIS_FRD_cogs/VHRDC_LIS_FRD_Month_"+number+"_co.tif"
    }else if(title === 'VHRAC'){
        API = "https://3ckzasvsu4.execute-api.us-west-2.amazonaws.com/development/singleband/VHRAC/"+number+"/LIS/{z}/{x}/{y}.png?colormap=terrain&stretch_range=[0.00010072781151393428,0.08138028532266617]"
        location = "https://innovation-netcdfs.s3.us-west-2.amazonaws.com/cogs/VHRAC_LIS_FRD_cogs/VHRAC_LIS_FRD_Month_"+number+"_co.tif"
    }else if(title === 'VHRSC'){
        API = "https://3ckzasvsu4.execute-api.us-west-2.amazonaws.com/development/singleband/VHRSC/"+number+"/LIS/{z}/{x}/{y}.png?colormap=terrain&stretch_range=[0.00010455249866936356,0.06766455620527267]"
        location = "https://innovation-netcdfs.s3.us-west-2.amazonaws.com/cogs/VHRSC_LIS_FRD_cogs/VHRSC_LIS_FRD_Month_"+number+"_co.tif"
    }

    return {
        id:Math.random().toString(),
        name:name,
        API:API,
        location:location,
        thumbnailURL:''
    }
}