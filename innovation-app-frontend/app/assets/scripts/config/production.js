// module exports is required to be able to load from gulpfile.
module.exports = {
  default: {
    environment: 'production',
    appTitle: 'Innovation App',
    appDescription: 'Welcome to Innovation App.',
    gaTrackingCode: 'UA-170089104-1',
    twitterHandle: '@NASAEarthData',
    mbToken: 'pk.eyJ1IjoiYWxhbnN1YmVkaSIsImEiOiJjbDF1eTJodzgwMWp2M2RxYzR3Mmlod3g3In0.bWeFglLhxIyJGT8ytNbvTw',
    api: 'https://8ib71h0627.execute-api.us-east-1.amazonaws.com/v1',
    map: {
      center: [0, 0],
      zoom: 2,
      minZoom: 1,
      maxZoom: 20,
      styleUrl: 'mapbox://styles/mapbox/satellite-streets-v11'
    }
  }
};


//mapbox://styles/covid-nasa/ckb01h6f10bn81iqg98ne0i2y

//mapbox://styles/mapbox/satellite-streets-v11