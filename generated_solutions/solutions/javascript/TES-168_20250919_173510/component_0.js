// solution.js
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

class SolutionHandler {
    constructor() {
        this.createdAt = new Date();
    }
    
    process(data) {
        console.log('Processing data:', data);
        return {
            status: 'success',
            data: data,
            timestamp: this.createdAt.toISOString()
        };
    }
    
    validateInput(data) {
        if (!data) {
            throw new Error('Data cannot be empty');
        }
        return true;
    }
}

const handler = new SolutionHandler();

app.get('/api/health', (req, res) => {
    res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.post('/api/process', (req, res) => {
    try {
        const result = handler.process(req.body);
        res.json(result);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});

module.exports = { SolutionHandler };