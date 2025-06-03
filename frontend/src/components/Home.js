import React, { useEffect, useState, useMemo, useContext } from 'react';
import Plot from 'react-plotly.js';
import { getSignals, triggerDataRetrieval } from '../api';
import { LoadingContext } from '../contexts/LoadingContext';

// Helper function to format numbers to 2 decimal places
function formatNumber(value) {
    if (value === "N/A" || value === undefined || value === null || isNaN(Number(value))) return '';
    return Number(value).toFixed(2);
}

function getCellClass(row, col) {
    if (col === 'Buy' && row.Buy === true) return 'positive-bg';
    if (col === 'Sell' && row.Sell === true) return 'negative-bg';
    if (col === 'close' && row.Buy === true) return 'positive-bg';
    if (col === 'close' && row.Sell === true) return 'negative-bg';
    if (col === 'sma' && row.sma > row.ema) return 'negative-text';
    if (col === 'ema' && row.ema > row.sma) return 'positive-text';
    if (col === 'rsi' && row.rsi > row.ma_rsi) return 'positive-text';
    if (col === 'ma_rsi' && row.ma_rsi > row.rsi) return 'negative-text';
    return '';
}

const Home = () => {
    const [data, setData] = useState({});
    const { setLoading } = useContext(LoadingContext);

    const updateData = async () => {
        setLoading(true);
        const signals = await getSignals();
        setData(signals);
        setLoading(false);
    };

    const triggerUpdate = async () => {
        setLoading(true);
        const response = await triggerDataRetrieval();
        alert(response.description || 'Data retrieval triggered ERROR');
        updateData();
    };

    useEffect(() => {
        updateData();
        // eslint-disable-next-line
    }, []);

    // Memoize plotData and plotLayout for performance
    const [plotData, plotLayout] = useMemo(() => {
        if (!data.data || !data.data.length) return [[], {}];

        const chartData = data.data;
        const times = chartData.map(d => d.time);
        const open = chartData.map(d => +d.open);
        const high = chartData.map(d => +d.high);
        const low = chartData.map(d => +d.low);
        const close = chartData.map(d => +d.close);
        const volume = chartData.map(d => +d.volume);
        const sma_1 = chartData.map(d => d.sma ? +d.sma : null);
        const ema_1 = chartData.map(d => d.ema ? +d.ema : null);
        const rsi_1 = chartData.map(d => d.rsi ? +d.rsi : null);
        const ma_rsi_1 = chartData.map(d => d.ma_rsi ? +d.ma_rsi : null);
        const buy = chartData.map(d => d.Buy);
        const sell = chartData.map(d => d.Sell);

        const ohlc = {
            x: times, open, high, low, close,
            type: 'candlestick', name: 'OHLC', yaxis: 'y1'
        };
        const sma = {
            x: times, y: sma_1, type: 'scatter', mode: 'lines',
            name: 'SMA 5', line: { color: 'orange', width: 1.5 }, yaxis: 'y1'
        };
        const ema = {
            x: times, y: ema_1, type: 'scatter', mode: 'lines',
            name: 'EMA 3', line: { color: 'blue', width: 1.5 }, yaxis: 'y1'
        };
        const vol = {
            x: times, y: volume, type: 'bar', name: 'Volume', yaxis: 'y2',
            marker: { color: 'rgba(100,100,200,0.3)' }, opacity: 0.5
        };
        const rsi_trace = {
            x: times, y: rsi_1, type: 'scatter', mode: 'lines',
            name: 'RSI', line: { color: 'green', width: 1.5 }, yaxis: 'y3'
        };
        const marsi_trace = {
            x: times, y: ma_rsi_1, type: 'scatter', mode: 'lines',
            name: 'MA-RSI', line: { color: 'red', width: 1.5 }, yaxis: 'y3'
        };

        const buyIndices = buy.map((b, i) => b ? i : -1).filter(i => i !== -1);
        const sellIndices = sell.map((s, i) => s ? i : -1).filter(i => i !== -1);

        const buy_x = buyIndices.map(i => times[i]);
        const buy_y = buyIndices.map(i => low[i] - (high[i] - low[i]) * 0.03);
        const sell_x = sellIndices.map(i => times[i]);
        const sell_y = sellIndices.map(i => high[i] + (high[i] - low[i]) * 0.03);

        const buy_arrows = {
            x: buy_x, y: buy_y, mode: 'markers', name: 'Buy', yaxis: 'y1',
            marker: {
                symbol: 'arrow-up', color: 'green', size: 18,
                line: { width: 1, color: 'black' }
            }, type: 'scatter'
        };
        const sell_arrows = {
            x: sell_x, y: sell_y, mode: 'markers', name: 'Sell', yaxis: 'y1',
            marker: {
                symbol: 'arrow-down', color: 'red', size: 18,
                line: { width: 1, color: 'black' }
            }, type: 'scatter'
        };

        const plotData = [
            ohlc, sma, ema, vol, buy_arrows, sell_arrows, rsi_trace, marsi_trace
        ];

        const plotLayout = {
            title: { text: 'VN30F1M Chart' },
            height: 1000,
            grid: { rows: 1, columns: 1 },
            xaxis: {
                title: 'Time',
                type: 'category',
                rangeslider: { visible: false },
                anchor: 'y3',
                tickangle: -45,
                automargin: true,
                showgrid: true,
                gridcolor: '#eee',
            },
            yaxis: {
                title: 'Price',
                domain: [0.3, 1],
                side: 'right'
            },
            yaxis2: {
                title: 'Volume',
                overlaying: 'y',
                side: 'left',
                showgrid: false,
                domain: [0.3, 1]
            },
            yaxis3: {
                title: 'RSI',
                domain: [0, 0.3],
                side: 'right',
                range: [0, 100]
            },
            shapes: [
                {
                    type: 'line', xref: 'paper', x0: 0, x1: 1,
                    yref: 'y3', y0: 30, y1: 30,
                    line: { color: 'gray', width: 0.5, dash: 'dash' }
                },
                {
                    type: 'line', xref: 'paper', x0: 0, x1: 1,
                    yref: 'y3', y0: 70, y1: 70,
                    line: { color: 'gray', width: 0.5, dash: 'dash' }
                }
            ],
        };

        return [plotData, plotLayout];
    }, [data.data]);

    return (
        <section id="vn30f1m">
            <h2>Signal table</h2>
            <div>
                <p>Last trigger: {data.last_triggered ?? 'N/A'}</p>
            </div>
            <div>
                <button className='btn-refresh' onClick={triggerUpdate}>Refresh</button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Source</th>
                        <th>Time</th>
                        <th>Open</th>
                        <th>High</th>
                        <th>Low</th>
                        <th>Close</th>
                        <th>Volume</th>
                        <th>SMA</th>
                        <th>EMA</th>
                        <th>RSI</th>
                        <th>MA RSI</th>
                        <th>Buy</th>
                        <th>Sell</th>
                    </tr>
                </thead>
                <tbody>
                    {data.data?.slice(-10).map((row, idx) => (
                        <tr key={idx}>
                            <td>{row.name}</td>
                            <td>{row.category}</td>
                            <td>{row.source}</td>
                            <td><strong>{row.time}</strong></td>
                            <td>{formatNumber(row.open)}</td>
                            <td>{formatNumber(row.high)}</td>
                            <td>{formatNumber(row.low)}</td>
                            <td className={getCellClass(row, 'close')}>{formatNumber(row.close)}</td>
                            <td>{formatNumber(row.volume)}</td>
                            <td className={getCellClass(row, 'sma')}>{formatNumber(row.sma)}</td>
                            <td className={getCellClass(row, 'ema')}>{formatNumber(row.ema)}</td>
                            <td className={getCellClass(row, 'rsi')}>{formatNumber(row.rsi)}</td>
                            <td className={getCellClass(row, 'ma_rsi')}>{formatNumber(row.ma_rsi)}</td>
                            <td className={getCellClass(row, 'Buy')}>{row.Buy ? 'Yes' : 'No'}</td>
                            <td className={getCellClass(row, 'Sell')}>{row.Sell ? 'Yes' : 'No'}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <h2>Signal Chart</h2>
            <Plot
                data={plotData}
                layout={plotLayout}
                useResizeHandler
                style={{ width: '100%', height: 1000 }}
                config={{ responsive: true }}
            />
        </section>
    );
};

export default Home;