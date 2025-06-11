import axios from 'axios';
import configs from './configs.json';

const getEndpoint = (endpoint) => {
    return `${configs.API_BASE_URL}${endpoint}`;
};

export const getSignals = async () => {
    try {
        const response = await axios.get(getEndpoint('signals'));
        return response.data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return {};
    }
};

export const getStocks = async () => {
    try {
        const response = await axios.get(getEndpoint('stocks'));
        return response.data;
    } catch (error) {
        console.error('Error fetching stocks:', error);
        return {};
    }
};

export const triggerDataRetrieval = async () => {
    try {
        const response = await axios.get(getEndpoint('build'));
        return response.data;
    } catch (error) {
        console.error('Error triggering data retrieval:', error);
        return {};
    }
};

export const filterStocks = async () => {
    try {
        const response = await axios.get(getEndpoint('filter'));
        return response.data;
    } catch (error) {
        console.error('Error filtering stocks:', error);
        return {};
    }
};