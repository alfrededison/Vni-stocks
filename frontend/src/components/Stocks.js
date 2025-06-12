import React, { useContext, useEffect, useState } from 'react';
import { filterStocks, getStocks } from '../api';
import { LoadingContext } from '../contexts/LoadingContext';

const Stocks = () => {
    const [data, setData] = useState([]);
    const { setLoading } = useContext(LoadingContext);

    const updateData = async () => {
        setLoading(true);
        const signals = await getStocks();
        setData(signals);
        setLoading(false);
    };

    const triggerUpdate = async () => {
        setLoading(true);
        const response = await filterStocks();
        alert(response.message || 'Stock filter triggered ERROR');
        updateData();
    }

    useEffect(() => {
        updateData();
        // eslint-disable-next-line
    }, []);

    function getStockCellClass(stock, col) {
        if (col === 'revenueGrowth1Year' && stock.revenueGrowth1Year >= 20) return 'positive-bg';
        if (col === 'revenueGrowth5Year' && stock.revenueGrowth5Year >= 20) return 'positive-bg';
        if (col === 'epsGrowth1Year' && stock.epsGrowth1Year >= 20) return 'positive-bg';
        if (col === 'epsGrowth5Year' && stock.epsGrowth5Year >= 20) return 'positive-bg';
        if (col === 'lastQuarterProfitGrowth' && stock.lastQuarterProfitGrowth >= 20) return 'positive-bg';
        if (col === 'secondQuarterProfitGrowth' && stock.secondQuarterProfitGrowth >= 20) return 'positive-bg';
        if (col === 'netMargin' && stock.netMargin >= 10) return 'positive-bg';
        if (col === 'avgTradingValue5Day' && stock.avgTradingValue5Day >= 10) return 'positive-bg';
        if (col === 'hasFinancialReport' && stock['hasFinancialReport.en'] === 'Yes') return 'positive-bg';
        if (col === 'hasFinancialReport' && stock['hasFinancialReport.en'] !== 'Yes') return 'negative-bg';
        if (col === 'relativeStrength3Day' && stock.relativeStrength3Day >= 80) return 'positive-bg';
        if (col === 'relativeStrength1Month' && stock.relativeStrength1Month >= 80) return 'positive-bg';
        return '';
    }

    return (
        <section id="vnstocks">
            <h1>Filtered Stocks</h1>
            <div>
                <p>Last Filtered: {data.last_filtered ?? 'N/A'} UTC</p>
                <p>Total: <strong>{data.total}</strong></p>
            </div>
            <div>
                <button className='btn-refresh' onClick={triggerUpdate}>Refresh</button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Financial Report</th>
                        <th>Revenue Growth (1Y)</th>
                        <th>Revenue Growth (5Y)</th>
                        <th>EPS Growth (1Y)</th>
                        <th>EPS Growth (5Y)</th>
                        <th>Last Q Profit Growth</th>
                        <th>2nd Q Profit Growth</th>
                        <th>Net Margin</th>
                        <th>Profit (Last 4Q)</th>
                        <th>Avg Trading Value (5D)</th>
                        <th>RS (3D)</th>
                        <th>RS (1M)</th>
                    </tr>
                </thead>
                <tbody>
                    {data.filtered_stocks?.map((stock, idx) => (
                        <tr key={stock.ticker || idx}>
                            <td>{stock.ticker}</td>
                            <td className={getStockCellClass(stock, 'hasFinancialReport')}>{stock["hasFinancialReport.en"]}</td>
                            <td className={getStockCellClass(stock, 'revenueGrowth1Year')}>{stock.revenueGrowth1Year}</td>
                            <td className={getStockCellClass(stock, 'revenueGrowth5Year')}>{stock.revenueGrowth5Year}</td>
                            <td className={getStockCellClass(stock, 'epsGrowth1Year')}>{stock.epsGrowth1Year}</td>
                            <td className={getStockCellClass(stock, 'epsGrowth5Year')}>{stock.epsGrowth5Year}</td>
                            <td className={getStockCellClass(stock, 'lastQuarterProfitGrowth')}>{stock.lastQuarterProfitGrowth}</td>
                            <td className={getStockCellClass(stock, 'secondQuarterProfitGrowth')}>{stock.secondQuarterProfitGrowth}</td>
                            <td className={getStockCellClass(stock, 'netMargin')}>{stock.netMargin}</td>
                            <td>{stock.profitForTheLast4Quarters}</td>
                            <td className={getStockCellClass(stock, 'avgTradingValue5Day')}>{stock.avgTradingValue5Day}</td>
                            <td className={getStockCellClass(stock, 'relativeStrength3Day')}>{stock.relativeStrength3Day}</td>
                            <td className={getStockCellClass(stock, 'relativeStrength1Month')}>{stock.relativeStrength1Month}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </section>
    );
};

export default Stocks;