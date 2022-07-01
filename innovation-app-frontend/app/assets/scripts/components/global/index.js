// this is the main initial page shown

import React, {useRef, useEffect} from 'react';
import T from 'prop-types';
import styled from 'styled-components';
import { withRouter } from 'react-router';
import App from '../common/app';
import ExpMapPrimePanel from './prime-panel';
import {
  Inpage,
  InpageHeader,
  InpageHeaderInner,
  InpageHeadline,
  InpageTitle,
  InpageBody
} from '../../styles/inpage';
import MbMap from '../common/mb-map-explore/mb-map';
import { themeVal } from '../../styles/utils/general';
import media from '../../styles/utils/media-queries';
import {
  getInitialMapExploreState,
} from '../../utils/map-explore-utils';

import Modal from '../../utils/Modal';

const ExploreCanvas = styled.div`
  display: grid;
  height: 100%;
  grid-template-columns: min-content 1fr min-content;
  overflow: hidden;

  ${media.mediumDown`
    ${({ panelPrime, panelSec }) => {
      if (panelPrime && !panelSec) {
        return 'grid-template-columns: min-content 0 0;';
      }

      if (!panelPrime && panelSec) {
        return 'grid-template-columns: 0 0 min-content;';
      }
    }}
  `}

  > * {
    grid-row: 1;
  }
`;

const ExploreCarto = styled.section`
  position: relative;
  height: 100%;
  background: ${themeVal('color.baseAlphaA')};
  display: grid;
  grid-template-rows: 1fr auto;
  min-width: 0;
  overflow: hidden;
`;


class GlobalExplore extends React.Component {
  constructor (props) {
    super(props);
    this.name = this.props.match.params.name;
    this.id = this.props.match.params.id;
    this.state = {
      ...getInitialMapExploreState(),
    };
  }

  componentWillUnmount () {
  }

  onPanelChange (panel, revealed) {
  }

  toggleCompare(passLayer){
  }

  updateUrlQS () {
  }

  onPanelAction (action, payload) {
  }

  async onMapAction (action, payload) {
  }

  toggleLayer (layer) {
  }

  render () {

    return (
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
            <ExploreCanvas>
              <ExpMapPrimePanel
              />
              <ExploreCarto>
                <MbMap
                  ref={this.mbMapRef}
                  position={this.state.mapPos}
                  onAction={this.onMapAction}
                  name={this.name}
                  id={this.id}
                  enableLocateUser
                  enableOverlayControls
                /> 
                <Modal/>
              </ExploreCarto>
            </ExploreCanvas>
          </InpageBody>
        </Inpage>
      </App>
    );
  }
}

GlobalExplore.propTypes = {
  invalidateCogTimeData: T.func,
  mapLayers: T.array,
  cogTimeData: T.object,
  spotlightList: T.object,
  location: T.object,
  history: T.object
};

export default withRouter(GlobalExplore);