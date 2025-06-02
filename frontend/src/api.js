import axios from 'axios';
import configs from './configs.json';

export const getSignals = async () => {
    try {
        const response = await axios.get(`${configs.API_BASE_URL}/signals`);
        return response.data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return {};
    }
};

export const getStocks = async () => {
    try {
        const response = await axios.get(`${configs.API_BASE_URL}/stocks`);
        return response.data;
    } catch (error) {
        console.error('Error fetching stocks:', error);
        return {};
    }
};

export const triggerDataRetrieval = async () => {
    try {
        const response = await axios.get(`${configs.API_BASE_URL}/build`);
        return response.data;
    } catch (error) {
        console.error('Error triggering data retrieval:', error);
        return {};
    }
};

export const filterStocks = async () => {
    try {
        const response = await axios.get(`${configs.API_BASE_URL}/filter`);
        return response.data;
    } catch (error) {
        console.error('Error filtering stocks:', error);
        return {};
    }
};