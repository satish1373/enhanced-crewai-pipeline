// test/solution.test.js
const { SolutionHandler } = require('../solution');

describe('SolutionHandler', () => {
    let handler;
    
    beforeEach(() => {
        handler = new SolutionHandler();
    });
    
    test('should process data successfully', () => {
        const result = handler.process('test data');
        expect(result.status).toBe('success');
        expect(result.data).toBe('test data');
    });
    
    test('should validate input correctly', () => {
        expect(handler.validateInput('valid')).toBe(true);
        expect(() => handler.validateInput('')).toThrow('Data cannot be empty');
    });
});