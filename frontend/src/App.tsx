import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Page, Masthead, MastheadMain, MastheadBrand } from '@patternfly/react-core';
import { Dashboard } from './pages/Dashboard';
import { RepositoryDetail } from './pages/RepositoryDetail';

function App() {
  const header = (
    <Masthead>
      <MastheadMain>
        <MastheadBrand href="/">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ fontSize: '1.5rem' }}>🚢</span>
            <span style={{ fontWeight: 'bold' }}>Ship-Shape Quality Profiling</span>
          </div>
        </MastheadBrand>
      </MastheadMain>
    </Masthead>
  );

  return (
    <Router>
      <Page header={header}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/repository/:repoUrl" element={<RepositoryDetail />} />
        </Routes>
      </Page>
    </Router>
  );
}

export default App;
