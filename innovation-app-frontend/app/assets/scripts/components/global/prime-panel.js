// left nav bar main file

import React from 'react';
import styled from 'styled-components';

import Panel from '../common/panel';

import media, { isLargeViewport } from '../../styles/utils/media-queries';

const PrimePanel = styled(Panel)`
  ${media.largeUp`
    width: 0rem;
  `}
`;

class ExpMapPrimePanel extends React.Component {

  render () {

    return (
        <PrimePanel
          //collapsible
        />
    );
  }
}

ExpMapPrimePanel.propTypes = {
};

export default ExpMapPrimePanel;
