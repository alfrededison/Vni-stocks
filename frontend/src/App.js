import React from 'react';
import { BrowserRouter as Router, Route, Switch, Link } from 'react-router-dom';
import Home from './components/Home';
import Stocks from './components/Stocks';
import './index.css';
import './table.css';

function App() {
    return (
        <Router>
            <header className="header-nav">
                <nav>
                    <Link to="/" style={{ marginRight: '1rem' }}>Home</Link>
                    <Link to="/stocks">Stocks</Link>
                </nav>
            </header>
            <Switch>
                <Route path="/" exact component={Home} />
                <Route path="/stocks" component={Stocks} />
            </Switch>
        </Router>
    );
}

export default App;