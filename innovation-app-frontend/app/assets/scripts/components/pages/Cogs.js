import React from "react";
import {
    Inpage,
    InpageHeader,
    InpageHeaderInner,
    InpageHeadline,
    InpageTitle,
    InpageBody
} from '../../styles/inpage';
import App from '../common/app';
import styled from 'styled-components';
import { useParams, useHistory } from "react-router-dom";
import {BsDownload} from '../../../../../node_modules/react-icons/bs'
import {getCOGS} from "./storeData";

const COGS = styled.button`
width:200px;
height:180px;
display:flex;
background-color:black;
background-image: url("https://wug8w3fg42.execute-api.us-west-2.amazonaws.com/development/singleband/VHRAC/2013_01_01/LIS/2/1/2.png?colormap=terrain&stretch_range=[0.00010455249866936356,0.06766455620527267]");
background-position: center; /* Center the image */
background-repeat: no-repeat; /* Do not repeat the image */
background-size: cover; /* Resize the background image to cover the entire container */
color:white;
margin:20px;
text-align:center;
align-items:center;
justify-content:center;
border-radius:25px;
text-transform:uppercase;
cursor:pointer;
:hover{
    box-shadow: 0px 2px 4px 4px green;
    color:green;
}
`

const Download = styled.div`
background-color:DodgerBlue;
height:30px;
width:100%;
margin-top:5px;
font-size: 20px;
font-weight:500;
display:flex;
border:2px solid black;
color:black;
:hover{
    cursor:pointer;
    background-color:RoyalBlue;
    color:black;
}
`
const Cogs = () =>{

    const params = useParams();
    const history = useHistory();
    const data = getCOGS(params.name)

    console.log(data)
    const clickHandler = (e) =>{
        history.push("/map/"+params.name+'/'+e.target.value)
    }

    const downloadHandler = () =>{

    }

    return(
        <App hideFooter>
            <Inpage isMapCentric>
            <InpageHeader>
                <InpageHeaderInner>
                <InpageHeadline>
                    <InpageTitle>Map</InpageTitle>
                </InpageHeadline>
                </InpageHeaderInner>
            </InpageHeader>
            <InpageBody>
                <div style={{display:'flex', width:'100vw', flexWrap:'wrap',alignItems:'center', flexDirection:'column', height:''}}>
                    <div style={{height:'100px', width:'100vw', textAlign:'center', justifyContent:'center', alignItems:'center', color:'black'}}><h1>COGS</h1></div>
                    <div style={{display:'flex', width:'60vw', flexWrap:'wrap', justifyContent:'center'}}>
                        {data.map((element)=>{
                            return (
                                <div style={{textAlign:'center', marginRight:'20px',display:'flex', flexDirection:'column', justifyContent:'center', alignContent:'center', alignItems:'center'}} key={element.name}>
                                    <COGS onClick={clickHandler} value={element.id} key={element.name} />
                                    <div style={{display:'flex', flexDirection:'column',justifyContent:'ceneter', textAlign:'center', alignItems:'center'}}>
                                        <h3>{element.name}</h3>
                                        <a href={element.location} style={{width:'100%'}}>
                                            <Download onClick={downloadHandler}>
                                                <div style={{marginRight:'20px', marginLeft:'10px', marginTop:'2px'}}>
                                                <BsDownload/>
                                                </div>
                                                <div style={{color:'black', fontSize:'20px', marginLeft:'10px'}}>Download</div>
                                            </Download>
                                        </a>
                                    </div>
                                </div>
                            )  
                        })}
                    </div>
                </div>
            </InpageBody>
            </Inpage>
        </App>
    )
}

export default Cogs