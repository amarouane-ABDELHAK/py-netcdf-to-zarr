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
import { useHistory, Link } from "react-router-dom";
import data from './data.json'
import { setData, getData, getFolders } from "./storeData";


const Directories = styled.button`
width:300px;
height:250px;
display:flex;
background-color:white;
border:none;
background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/OneDrive_Folder_Icon.svg/1200px-OneDrive_Folder_Icon.svg.png");
background-position: center; /* Center the image */
background-repeat: no-repeat; /* Do not repeat the image */
background-size: cover; /* Resize the background image to cover the entire container */
color:black;
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
const Home = () =>{

    const arr = getFolders();

    let history = useHistory()

    const clickHandler = (e) =>{
        history.push("/COGS/"+e.target.value)
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
                    <div style={{height:'100px', width:'100vw', textAlign:'center', justifyContent:'center', alignItems:'center', color:'black'}}><h1>Files</h1></div>
                    <div style={{display:'flex', width:'60vw', flexWrap:'wrap', justifyContent:'center'}}>
                        {arr.map((element)=>(
                            <Link to={'/COGS/'+element} key={element}><Directories value={element}>{element}</Directories></Link>
                        ))}
                    </div>
                </div>
            </InpageBody>
            </Inpage>
        </App>
    )
}

export default Home