import React,{useState, useEffect} from 'react';
import styled, { withTheme, ThemeProvider } from 'styled-components';
import ReactDOM from 'react-dom'

const ModalBackground = styled.div`
width: 100vw;
height: 100vh;
background-color:white;
//background-color: rgba(200, 200, 200,0.6);
position: relative;
display: flex;
justify-content: center;
align-items: center;
z-index:999999;
bottom:100vh;
//border-radius: 12px;
`
const Button = styled.button`
position:absolute;
z-index:10000;
top:1rem;
right:1rem;
padding:5px;
cursor:pointer;
background-color: Transparent;
background-repeat:no-repeat;
border: none;
font-weight:bold;
`
const Backward = styled.button`
position:absolute;
z-index:10000;
top:45%;
left:1rem;
padding:5px;
cursor:pointer;
//border-radius:50%;
padding:30px;
height:50px;
width:50px;
font-weight:bold;
border:1px solid;
font-size: 40px;

background-color: Transparent;
background-repeat:no-repeat;
border: none;
// font-weight:bold;
`
const Forward = styled.button`
position:absolute;
z-index:10000;
top:45%;
right:1rem;
padding:5px;
cursor:pointer;
//border-radius:50%;
padding:30px;
height:50px;
width:50px;
font-weight:bold;
border:1px solid;
font-size: 40px;

background-color: Transparent;
background-repeat:no-repeat;
border: none;
// font-weight:bold;
`

const ImageContainer = styled.div`
background-image:url(${(props)=>props.background})
// background-repeat: no-repeat;
`

const Modal = (props) =>{

    const [modal, setModal] = useState(true)
    
    useEffect(()=>{
        let timer = setTimeout(()=>setModal(false), 2500)
        return ()=>{
            clearTimeout(timer);
        }
    })

    return ReactDOM.createPortal(
        <>
            {
            modal &&
            <ModalBackground>
                <div style={{display:'flex', flexDirection:'column', justifyContent:'center', alignItems:'center'}}>
                    <img src="https://raw.githubusercontent.com/Codelessly/FlutterLoadingGIFs/master/packages/cupertino_activity_indicator.gif" alt="Loading" width="100" height="100" style={{marginBottom:"30px"}}></img>
                    <h2>Loading GEOTIFF images...</h2>
                </div>
            </ModalBackground>        
            }
        </>
        ,document.getElementById('portal')
    )
}

export default Modal