import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch, Link } from 'react-router-dom';
import Home from './components/Home';
import Stocks from './components/Stocks';
import { LoadingContext } from './contexts/LoadingContext';
import './index.css';
import './table.css';

function App() {
    const [loading, setLoading] = useState(false);

    return (
        <LoadingContext.Provider value={{ loading, setLoading }}>
            <Router>
                {loading && (
                    <div className="loading-overlay">
                        <div className="loading-spinner"></div>
                    </div>
                )}
                <header className="header-nav">
                    <nav>
                        <Link to="/" style={{ marginRight: '1rem' }}>Home</Link>
                        <Link to="/stocks">Stocks</Link>
                    </nav>
                </header>
                <Switch>
                    <Route path="/" exact>
                        <Home />
                    </Route>
                    <Route path="/stocks">
                        <Stocks />
                    </Route>
                </Switch>
            </Router>
        </LoadingContext.Provider>
    );
}

export default App;