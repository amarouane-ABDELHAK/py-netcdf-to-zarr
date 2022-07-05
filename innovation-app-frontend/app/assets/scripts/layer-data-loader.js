import '@babel/polyfill';
import React from 'react';
import T from 'prop-types';
import { connect } from 'react-redux';

import config from './config';
import { fetchJSON, wrapApiResult } from './redux/reduxeed';
import {setData} from './components/pages/storeData';
import {filetoJSON} from './utils/HelperMethod';

class LayerDataLoader extends React.Component {
  componentDidMount () {
    this.requestData();
  }

  componentDidUpdate (prevProps) {
    // if (spotlightList.isReady() && !prevProps.spotlightList.isReady()) {
    //   this.requestData();
    // }
    console.log('im in pudate')
    //this.requestData();
  }

  async requestData () {


    const response = await fetch("http://localhost:3056/data")
    const data = await response.json();

    //setData(data.files)
    setData(filetoJSON(data))
    //console.log(data.files)
    //console.log(data.files[0].COGS.length)
    this.props.onReady();
  }


  render () {
    console.log('wassup')
    return null;
  }
}

LayerDataLoader.propTypes = {
  spotlightList: T.object,
  onReady: T.func
};

function mapStateToProps (state, props) {
  return {
    spotlightList: wrapApiResult(state.spotlight.list)
  };
}

export default connect(mapStateToProps, {})(LayerDataLoader);